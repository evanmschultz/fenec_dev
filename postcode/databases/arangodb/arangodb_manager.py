import logging
from typing import Any, Callable, Union

from arango.result import Result
from arango.cursor import Cursor
from arango.graph import Graph

from postcode.databases.arangodb.arangodb_connector import ArangoDBConnector
# from postcode.types.postcode import ModelType
from postcode.models.models import ClassModel, FunctionModel, ModuleModel, StandaloneCodeBlockModel
import postcode.databases.arangodb.helper_functions as helper_functions

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]

# NOTE: Remember, when adding logic to connect dependencies, the `from` the external dependency `to` the internal definition using it
 

class ArangoDBManager:
    def __init__(
        self,
        db_manager: ArangoDBConnector,
        default_graph_name: str = "codebase_graph",
    ) -> None:
        self.db_manager: ArangoDBConnector = db_manager

        self.processed_id_set = set()
        self.default_graph_name: str = default_graph_name

    def upsert_models(self, module_models: list[ModuleModel]) -> "ArangoDBManager":
        for model in module_models:
            self._upsert_model(model)
        return self

    def _upsert_model(self, module_model: ModuleModel) -> None:
        self._upsert_vertex(module_model, "modules")
        self._process_children(module_model)

    def _process_children(self, parent_model: ModelType) -> None:
        if not parent_model.children:
            return None

        for child in parent_model.children:
            if child.id in self.processed_id_set:
                continue

            self.processed_id_set.add(child.id)
            self._upsert_vertex(
                child, helper_functions.pluralize_block_type(child.block_type)
            )

            if child.children:
                self._process_children(child)

    def _upsert_vertex(self, model: ModelType, collection_name: str) -> None:
        model_data: dict[str, Any] = model.model_dump()
        model_data["_key"] = model.id

        try:
            self.db_manager.ensure_collection(
                collection_name, model.model_json_schema()
            )
            query: str = f"""
            UPSERT {{_key: @key}}
            INSERT @doc
            UPDATE @doc
            IN {collection_name}
            """
            bind_vars: dict[str, Any] = {"key": model.id, "doc": model_data}
            self.db_manager.db.aql.execute(query, bind_vars=bind_vars)

            if not isinstance(model, ModuleModel) and model.parent_id:
                parent_type: str = self._get_collection_from_id(model.parent_id)
                self._upsert_edge(
                    model.id, model.parent_id, collection_name, parent_type
                )
        except Exception as e:
            logging.error(f"Error upserting {collection_name} vertex (ArangoDB): {e}")

    def _upsert_edge(
        self, from_key: str, to_key: str, source_type: str, target_type: str
    ) -> None:
        source_string: str = f"{source_type}/{from_key}"
        target_string: str = f"{target_type}/{to_key}"

        edge_data: dict[str, str] = {
            "_from": source_string,
            "_to": target_string,
            "source_type": source_type,
            "target_type": target_type,
        }

        try:
            self.db_manager.ensure_edge_collection("code_edges")
            query = f"""
            UPSERT {{_from: @from, _to: @to}}
            INSERT @doc
            UPDATE @doc
            IN code_edges
            """
            bind_vars = {
                "from": edge_data["_from"],
                "to": edge_data["_to"],
                "doc": edge_data,
            }
            self.db_manager.db.aql.execute(query, bind_vars=bind_vars)
        except Exception as e:
            logging.error(f"Error upserting edge (ArangoDB): {e}")

    def _get_collection_from_id(self, block_id: str) -> str:
        block_id_parts: list[str] = block_id.split("__*__")
        block_type_part: str = block_id_parts[-1]

        block_type_functions: dict[str, Callable[..., str]] = {
            "MODULE": lambda: "modules",
            "CLASS": lambda: "classes",
            "FUNCTION": lambda: "functions",
            "STANDALONE_BLOCK": lambda: "standalone_blocks",
        }

        for key, func in block_type_functions.items():
            if block_type_part.startswith(key):
                return func()

        return "unknown"

    def process_imports_and_dependencies(self) -> "ArangoDBManager":
        for vertex_collection in helper_functions.pluralized_and_lowered_block_types():
            cursor: Result[Cursor] = self.db_manager.db.collection(
                vertex_collection
            ).all()
            if isinstance(cursor, Cursor):
                for vertex in cursor:
                    vertex_key = vertex["_key"]
                    if vertex_collection == "modules":
                        self._create_edges_for_imports(
                            vertex_key, vertex.get("imports", [])
                        )
                    else:
                        self._create_edges_for_dependencies(
                            vertex_key, vertex.get("dependencies", [])
                        )
            else:
                logging.error(
                    f"Error getting cursor for vertex collection: {vertex_collection}"
                )
        return self

    def _create_edges_for_imports(
        self, module_key: str, imports: list[dict[str, Any]]
    ) -> None:
        if not imports:
            logging.debug(f"No imports found for module {module_key}")
            return

        logging.info(f"Processing imports for module {module_key}")

        for _import in imports:
            import_names: list[dict[str, str]] = _import.get("import_names", [])
            if not import_names:
                logging.debug(f"No import names found in import {_import}")
                continue

            for import_name in import_names:
                local_block_id: str | None = import_name.get("local_block_id")

                if local_block_id:
                    target_type = self._get_collection_from_id(local_block_id)
                    try:
                        self._upsert_edge(
                            local_block_id, module_key, target_type, "modules"
                        )

                        logging.info(
                            f"Upserted edge for import {module_key} to {local_block_id}"
                        )
                    except Exception as e:
                        logging.error(
                            f"Error creating edge for import {module_key} to {local_block_id}: {e}"
                        )
                else:
                    logging.warning(
                        f"Skipped import {import_name} in module {module_key}"
                    )

    def _create_edges_for_dependencies(
        self, block_key: str, dependencies: list[dict[str, Any]]
    ) -> None:
        if not dependencies:
            return

        for dependency in dependencies:
            code_block_id: str | None = dependency.get("code_block_id")
            if code_block_id:
                source_type: str = self._get_collection_from_id(code_block_id)
                target_type: str = self._get_collection_from_id(block_key)
                try:
                    self._upsert_edge(
                        code_block_id, block_key, source_type, target_type
                    )
                    logging.info(
                        f"Upserted edge for dependency {block_key} to {code_block_id}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error creating edge for dependency {block_key} to {code_block_id}: {e}"
                    )

    def delete_vertex_by_id(
        self, vertex_key: str, graph_name: str | None = None
    ) -> None:
        collection_name: str = self._get_collection_from_id(vertex_key)
        if collection_name == "unknown":
            logging.error(f"Unknown vertex type for key: {vertex_key}")
            return None

        if not graph_name:
            graph_name = self.default_graph_name

        try:
            vertex_coll = self.db_manager.db.graph(graph_name).vertex_collection(
                collection_name
            )

            vertex_coll.delete(vertex_key)

            logging.info(
                f"Vertex '{vertex_key}' from collection '{collection_name}' was successfully deleted."
            )

        except Exception as e:
            logging.error(
                f"Error deleting vertex '{vertex_key}' from collection '{collection_name}': {e}"
            )

    def get_graph(self, graph_name: str | None = None) -> Graph | None:
        if not graph_name:
            graph_name = self.default_graph_name
        try:
            return self.db_manager.db.graph(self.default_graph_name)
        except Exception as e:
            logging.error(f"Error getting graph '{self.default_graph_name}': {e}")
            return None

    def get_or_create_graph(self, graph_name: str | None = None) -> Result[Graph]:
        if not graph_name:
            graph_name = self.default_graph_name

        try:
            if not self.db_manager.db.has_graph(graph_name):
                edge_definitions: list[dict[str, str | list[str]]] = [
                    {
                        "edge_collection": "code_edges",
                        "from_vertex_collections": helper_functions.pluralized_and_lowered_block_types(),
                        "to_vertex_collections": helper_functions.pluralized_and_lowered_block_types(),
                    }
                ]

                logging.info(f"Graph '{graph_name}' created successfully.")
                return self.db_manager.db.create_graph(
                    graph_name, edge_definitions=edge_definitions
                )

            else:
                return self.get_graph()

        except Exception as e:
            logging.error(f"Error creating graph '{graph_name}': {e}")

    def delete_graph(self, graph_name: str | None = None) -> None:
        if not graph_name:
            graph_name = self.default_graph_name
        try:
            self.db_manager.db.delete_graph(graph_name)
            logging.info(f"Graph '{graph_name}' deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting graph '{graph_name}': {e}")

    def get_outbound_models(self, start_key: str) -> list[ModelType] | None:
        vertex_type: str = self._get_collection_from_id(start_key)

        query: str = f"""
        FOR v, e, p IN 1..100 OUTBOUND '{vertex_type}/{start_key}' GRAPH '{self.default_graph_name}'
        RETURN DISTINCT v
        """
        # query: str = f"""
        # FOR v, e, p IN 1..100 OUTBOUND '{vertex_type}/{start_key}' GRAPH '{self.default_graph_name}'
        # FILTER LENGTH(p.edges[* FILTER CURRENT != e]) == 0
        # RETURN DISTINCT v
        # """
        # query: str = f"""
        # FOR v, e, p IN 1..100 OUTBOUND '{vertex_type}/{start_key}' GRAPH '{self.default_graph_name}'
        # FILTER LENGTH(p.edges[* FILTER CURRENT != e]) == 0
        #     AND p.edges[*].distance ALL == 1
        # RETURN DISTINCT v
        # """

        try:
            cursor = self.db_manager.db.aql.execute(query)
            if isinstance(cursor, Cursor):
                return [
                    helper_functions.create_model_from_vertex(doc) for doc in cursor
                ]
            else:
                logging.error(f"Error getting cursor for query: {query}")
                return None
        except Exception as e:
            logging.error(f"Error in get_all_downstream_vertices: {e}")
            return None

    def get_inbound_models(self, end_key: str) -> list[ModelType] | None:
        vertex_type: str = self._get_collection_from_id(end_key)

        query: str = f"""
        FOR v, e, p IN 1..100 INBOUND '{vertex_type}/{end_key}' GRAPH '{self.default_graph_name}'
        RETURN DISTINCT v
        """

        # query: str = f"""
        # FOR v, e, p IN 1..100 INBOUND '{vertex_type}/{end_key}' GRAPH '{self.default_graph_name}'
        # FILTER LENGTH(p.edges[* FILTER CURRENT != e]) == 0
        # RETURN DISTINCT v
        # """

        try:
            cursor: Result[Cursor] = self.db_manager.db.aql.execute(query)
            if isinstance(cursor, Cursor):
                return [
                    helper_functions.create_model_from_vertex(doc) for doc in cursor
                ]
            else:
                logging.error(f"Error getting cursor for query: {query}")
                return None
        except Exception as e:
            logging.error(f"Error in get_all_upstream_vertices: {e}")
            return None
