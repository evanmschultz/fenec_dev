import logging
from typing import Any, Callable

from arango.result import Result
from arango.cursor import Cursor
from arango.graph import Graph

from postcode.databases.arangodb.arangodb_connector import ArangoDBConnector
from postcode.types.postcode import ModelType
from postcode.models.models import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
)
import postcode.databases.arangodb.helper_functions as helper_functions

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

    def insert_models(self, module_models: list[ModuleModel]) -> "ArangoDBManager":
        for model in module_models:
            self._process_model(model)
        return self

    def _process_model(self, module_model: ModuleModel) -> None:
        self._create_vertex_for_module(module_model)
        self._process_children(module_model)

    def _create_vertex_for_module(self, module_model: ModuleModel) -> None:
        module_data: dict[str, Any] = module_model.model_dump()
        module_data["_key"] = module_model.id

        try:
            self.db_manager.db.collection("modules").insert(module_data)
        except Exception as e:
            logging.error(f"Error inserting {module_model.id} vertex (ArangoDB): {e}")

    def _process_children(self, parent_model: ModelType) -> None:
        if not parent_model.children:
            return

        for child in parent_model.children:
            if child.id in self.processed_id_set:
                # logging.warning(f"Duplicate child key: {child.id}")
                continue

            self.processed_id_set.add(child.id)
            if isinstance(child, ClassModel):
                self._create_vertex_for_class(child)

            elif isinstance(child, FunctionModel):
                self._create_vertex_for_function(child)

            elif isinstance(child, StandaloneCodeBlockModel):
                self._create_vertex_for_standalone_block(child)

            if child.children:
                self._process_children(child)

    def _create_vertex(self, model: ModelType, vertex_type: str) -> None:
        if not model.parent_id:
            logging.error(f"Error: No parent id found for {model.id}")
            return None

        try:
            vertex_type_str: str = (
                f"{vertex_type}s" if not vertex_type == "class" else f"{vertex_type}es"
            )
            model_data: dict[str, Any] = model.model_dump()
            model_data["_key"] = model.id
            self.db_manager.ensure_collection(
                f"{vertex_type_str}", model.model_json_schema()
            )
            self.db_manager.db.collection(f"{vertex_type_str}").insert(model_data)

            parent_type: str = self._get_block_type_from_id(model.parent_id)
            self._create_edge(model.id, model.parent_id, vertex_type, parent_type)
        except Exception as e:
            logging.error(f"Error inserting {vertex_type} vertex (ArangoDB): {e}")

    def _create_vertex_for_class(self, class_data: ClassModel) -> None:
        self._create_vertex(class_data, "class")

    def _create_vertex_for_function(self, function_data: FunctionModel) -> None:
        self._create_vertex(function_data, "function")

    def _create_vertex_for_standalone_block(
        self, standalone_block_data: StandaloneCodeBlockModel
    ) -> None:
        self._create_vertex(standalone_block_data, "standalone_block")

    def _create_edge(
        self, from_key: str, to_key: str, source_type: str, target_type: str
    ) -> None:
        source_string: str = (
            f"{source_type}s/{from_key}"
            if not source_type == "class"
            else f"{source_type}es/{from_key}"
        )
        target_string: str = (
            f"{target_type}s/{to_key}"
            if not target_type == "class"
            else f"{target_type}es/{to_key}"
        )
        edge_data: dict[str, str] = {
            "_from": f"{source_string}",
            "_to": f"{target_string}",
            "source_type": source_type,
            "target_type": target_type,
        }
        try:
            self.db_manager.ensure_edge_collection("code_edges")
            self.db_manager.db.collection("code_edges").insert(edge_data)
        except Exception as e:
            logging.error(f"Error creating edge (ArangoDB): {e}")

    def _get_block_type_from_id(self, block_id: str) -> str:
        block_id_parts: list[str] = block_id.split("__*__")
        block_type_part: str = block_id_parts[-1]

        block_type_functions: dict[str, Callable[..., str]] = {
            "MODULE": lambda: "module",
            "CLASS": lambda: "class",
            "FUNCTION": lambda: "function",
            "STANDALONE_BLOCK": lambda: "standalone_block",
        }

        for key, func in block_type_functions.items():
            if block_type_part.startswith(key):
                return func()

        return "unknown"

    def process_imports_and_dependencies(self) -> "ArangoDBManager":
        # Process each vertex in the database
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
                    target_type = self._get_block_type_from_id(local_block_id)
                    try:
                        self._create_edge(
                            local_block_id, module_key, target_type, "module"
                        )
                        logging.debug(
                            f"Created edge for import {module_key} to {local_block_id}"
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
                source_type: str = self._get_block_type_from_id(code_block_id)
                target_type: str = self._get_block_type_from_id(block_key)
                try:
                    self._create_edge(
                        code_block_id, block_key, source_type, target_type
                    )
                except Exception as e:
                    logging.error(
                        f"Error creating edge for dependency {block_key} to {code_block_id}: {e}"
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
        vertex_type: str = self._get_block_type_from_id(start_key)
        if vertex_type == "class":
            vertex_type += "es"
        else:
            vertex_type += "s"

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
        vertex_type: str = self._get_block_type_from_id(end_key)
        if vertex_type == "class":
            vertex_type += "es"
        else:
            vertex_type += "s"

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
