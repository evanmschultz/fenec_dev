import logging
from typing import Any, Callable

from arango.result import Result
from arango.cursor import Cursor
from arango.graph import Graph
from arango.collection import StandardCollection
from arango.typings import Json

from fenec.databases.arangodb.arangodb_connector import ArangoDBConnector

from fenec.types.fenec import ModelType
from fenec.models.models import (
    ClassModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
)
import fenec.databases.arangodb.helper_functions as helper_functions

# NOTE: Remember, when adding logic to connect dependencies, the `from` the external dependency `to` the internal definition using it


class ArangoDBManager:
    """
    A manager class for handling interactions between the application and ArangoDB.

    This class provides methods for upserting models into ArangoDB, creating edges, processing imports and dependencies, deleting vertices, and querying the graph for related models.

    Attributes:
        - db_connector (ArangoDBConnector): The ArangoDB connector instance used for database interactions.
        - default_graph_name (str): The default graph name used for graph-related operations.

    Example:
        ```python
        # This example demonstrates how to use ArangoDBManager to upsert models and create edges in ArangoDB.
        connector = ArangoDBConnector(url="http://localhost:8529", username="root", password="openSesame", db_name="fenec")
        manager = ArangoDBManager(db_connector=connector)
        models_to_upsert = [ModuleModel(id="module_1", name="Module 1"), FunctionModel(id="function_1", name="Function 1")]
        manager.upsert_models(models_to_upsert)
        ```

    Methods:
        - upsert_models(module_models): Upserts a list of models into the ArangoDB database.
        - process_imports_and_dependencies(): Processes the imports and dependencies in the ArangoDB database, creating edges accordingly.
        - delete_vertex_by_id(vertex_key, graph_name=None): Deletes a vertex from the graph by its key.
        - get_graph(graph_name=None): Retrieves a graph instance by its name.
        - get_or_create_graph(graph_name=None): Retrieves an existing graph or creates a new one if not present.
        - delete_graph(graph_name=None): Deletes a graph by its name.
        - get_outbound_models(start_key): Retrieves all outbound models from a given starting key.
        - get_inbound_models(end_key): Retrieves all inbound models to a given ending key.
        - get_vertex_model_by_id(id): Retrieves a vertex model by its ID.
        - update_vertex_summary_by_id(id, new_summary): Updates the summary of a vertex by its ID.
        - get_all_modules(): Retrieves all modules from the graph.
        - get_all_vertices(): Retrieves all vertices from the graph.
    """

    def __init__(
        self,
        db_connector: ArangoDBConnector,
        default_graph_name: str = "codebase_graph",
    ) -> None:
        self.db_connector: ArangoDBConnector = db_connector

        self.processed_id_set = set()
        self.default_graph_name: str = default_graph_name

    def upsert_models(self, module_models: list[ModelType]) -> "ArangoDBManager":
        """
        Upserts a list of models into the ArangoDB database.

        Args:
            - module_models (list[ModelType]): The list of models to be upserted.

        Returns:
            - ArangoDBManager: The ArangoDBManager instance.
        """

        for model in module_models:
            self._upsert_model(model)
        return self

    def _upsert_model(self, model: ModelType) -> None:
        """
        Upserts a single model into the ArangoDB database.

        Args:
            - model (ModelType): The model to be upserted.
        """

        collection_name: str = self._get_collection_name_from_id(model.id)
        self._upsert_vertex(model, collection_name)

    def _upsert_vertex(self, model: ModelType, collection_name: str) -> None:
        """
        Upserts a vertex (document) into the specified collection in the ArangoDB database.

        Args:
            - model (ModelType): The model representing the vertex.
            - collection_name (str): The name of the collection.
        """

        model_data: dict[str, Any] = model.model_dump()
        model_data["_key"] = model.id

        try:
            self.db_connector.ensure_collection(
                collection_name, model.model_json_schema()
            )
            query: str = f"""
            UPSERT {{_key: @key}}
            INSERT @doc
            UPDATE @doc
            IN {collection_name}
            """
            bind_vars: dict[str, Any] = {"key": model.id, "doc": model_data}
            self.db_connector.db.aql.execute(query, bind_vars=bind_vars)

            if not isinstance(model, ModuleModel) and model.parent_id:
                parent_type: str = self._get_collection_name_from_id(model.parent_id)
                self._upsert_edge(
                    model.id, model.parent_id, collection_name, parent_type
                )
        except Exception as e:
            logging.error(f"Error upserting {collection_name} vertex (ArangoDB): {e}")

    def _upsert_edge(
        self, from_key: str, to_key: str, source_type: str, target_type: str
    ) -> None:
        """
        Upserts an edge between two vertices in the ArangoDB database.

        Args:
            - from_key (str): The key of the source vertex.
            - to_key (str): The key of the target vertex.
            - source_type (str): The type of the source vertex.
            - target_type (str): The type of the target vertex.
        """

        source_string: str = f"{source_type}/{from_key}"
        target_string: str = f"{target_type}/{to_key}"

        edge_data: dict[str, str] = {
            "_from": source_string,
            "_to": target_string,
            "source_type": source_type,
            "target_type": target_type,
        }

        try:
            self.db_connector.ensure_edge_collection("code_edges")
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
            self.db_connector.db.aql.execute(query, bind_vars=bind_vars)
        except Exception as e:
            logging.error(f"Error upserting edge (ArangoDB): {e}")

    def _get_collection_name_from_id(self, block_id: str) -> str:
        """
        Gets the collection name based on the block ID.

        Args:
            - block_id (str): The ID of the block.

        Returns:
            - str: The name of the collection.
        """

        block_id_parts: list[str] = block_id.split("__*__")
        block_type_part: str = block_id_parts[-1]

        block_type_functions: dict[str, Callable[..., str]] = {
            "MODULE": lambda: "modules",
            "CLASS": lambda: "classes",
            "FUNCTION": lambda: "functions",
            "STANDALONE_BLOCK": lambda: "standalone_blocks",
            "DIRECTORY": lambda: "directories",
        }

        for key, func in block_type_functions.items():
            if block_type_part.startswith(key):
                return func()

        return "unknown"

    def process_imports_and_dependencies(self) -> "ArangoDBManager":
        """
        Processes the imports and dependencies in the ArangoDB database, creating edges accordingly.

        Returns:
            - ArangoDBManager: The ArangoDBManager instance.
        """

        for vertex_collection in helper_functions.pluralized_and_lowered_block_types():
            cursor: Result[Cursor] = self.db_connector.db.collection(
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
        """
        Creates edges in the graph for the given module's imports.

        Args:
            - module_key (str): The key of the module for which imports are processed.
            - imports (list[dict[str, Any]]): The list of import information.
        """

        if not imports:
            # logging.debug(f"No imports found for module {module_key}")
            return

        # logging.info(f"Processing imports for module {module_key}")

        for _import in imports:
            import_names: list[dict[str, str]] = _import.get("import_names", [])
            if not import_names:
                # logging.debug(f"No import names found in import {_import}")
                continue

            for import_name in import_names:
                local_block_id: str | None = import_name.get("local_block_id")

                if local_block_id:
                    target_type = self._get_collection_name_from_id(local_block_id)
                    try:
                        self._upsert_edge(
                            local_block_id, module_key, target_type, "modules"
                        )

                        # logging.info(
                        #     f"Upserted edge for import {module_key} to {local_block_id}"
                        # )
                    except Exception as e:
                        logging.error(
                            f"Error creating edge for import {module_key} to {local_block_id}: {e}"
                        )
                else:
                    # logging.warning(
                    #     f"Skipped import {import_name} in module {module_key}"
                    # )
                    ...

    def _create_edges_for_dependencies(
        self, block_key: str, dependencies: list[dict[str, Any]]
    ) -> None:
        """
        Creates edges in the graph for the given block's dependencies.

        Args:
            - block_key (str): The key of the block for which dependencies are processed.
            - dependencies (list[dict[str, Any]]): The list of dependency information.
        """

        if not dependencies:
            return

        for dependency in dependencies:
            code_block_id: str | None = dependency.get("code_block_id")
            if code_block_id:
                source_type: str = self._get_collection_name_from_id(code_block_id)
                target_type: str = self._get_collection_name_from_id(block_key)
                try:
                    self._upsert_edge(
                        code_block_id, block_key, source_type, target_type
                    )
                    # logging.info(
                    #     f"Upserted edge for dependency {block_key} to {code_block_id}"
                    # )
                except Exception as e:
                    logging.error(
                        f"Error creating edge for dependency {block_key} to {code_block_id}: {e}"
                    )

    def delete_vertex_by_id(
        self, vertex_key: str, graph_name: str | None = None
    ) -> None:
        """
        Deletes a vertex from the graph by its key.

        Args:
            - vertex_key (str): The key of the vertex to be deleted.
            - graph_name (str, optional): The name of the graph. Defaults to None.
        """

        collection_name: str = self._get_collection_name_from_id(vertex_key)
        if collection_name == "unknown":
            logging.error(f"Unknown vertex type for key: {vertex_key}")
            return None

        if not graph_name:
            graph_name = self.default_graph_name

        try:
            vertex_coll = self.db_connector.db.graph(graph_name).vertex_collection(
                collection_name
            )

            vertex_coll.delete(vertex_key)

            # logging.info(
            #     f"Vertex '{vertex_key}' from collection '{collection_name}' was successfully deleted."
            # )

        except Exception as e:
            logging.error(
                f"Error deleting vertex '{vertex_key}' from collection '{collection_name}': {e}"
            )

    def get_graph(self, graph_name: str | None = None) -> Graph | None:
        """
        Retrieves a graph instance by its name.

        Args:
            - graph_name (str, optional): The name of the graph. Defaults to None.

        Returns:
            - Graph | None: The graph instance or None if not found.
        """

        if not graph_name:
            graph_name = self.default_graph_name
        try:
            return self.db_connector.db.graph(self.default_graph_name)
        except Exception as e:
            logging.error(f"Error getting graph '{self.default_graph_name}': {e}")
            return None

    def get_or_create_graph(self, graph_name: str | None = None) -> Result[Graph]:
        """
        Retrieves an existing graph or creates a new one if not present.

        Args:
            - graph_name (str, optional): The name of the graph. Defaults to None.

        Returns:
            - Result[Graph]: The result of the operation.
        """

        if not graph_name:
            graph_name = self.default_graph_name

        try:
            if not self.db_connector.db.has_graph(graph_name):
                edge_definitions: list[dict[str, str | list[str]]] = [
                    {
                        "edge_collection": "code_edges",
                        "from_vertex_collections": helper_functions.pluralized_and_lowered_block_types(),
                        "to_vertex_collections": helper_functions.pluralized_and_lowered_block_types(),
                    }
                ]

                # logging.info(f"Graph '{graph_name}' created successfully.")
                return self.db_connector.db.create_graph(
                    graph_name, edge_definitions=edge_definitions
                )

            else:
                return self.get_graph()

        except Exception as e:
            logging.error(f"Error creating graph '{graph_name}': {e}")

    def delete_graph(self, graph_name: str | None = None) -> None:
        """
        Deletes a graph by its name.

        Args:
            - graph_name (str, optional): The name of the graph. Defaults to None.
        """

        if not graph_name:
            graph_name = self.default_graph_name
        try:
            self.db_connector.db.delete_graph(graph_name)
            logging.info(f"Graph '{graph_name}' deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting graph '{graph_name}': {e}")

    def get_outbound_models(self, start_key: str) -> list[ModelType] | None:
        """
        Retrieves all outbound models from a given starting key.

        Args:
            - start_key (str): The key of the starting vertex.

        Returns:
            - list[ModelType] | None: List of outbound models or None if an error occurs.
        """

        vertex_type: str = self._get_collection_name_from_id(start_key)

        query: str = f"""
        FOR v, e, p IN 1..100 OUTBOUND '{vertex_type}/{start_key}' GRAPH '{self.default_graph_name}'
        RETURN DISTINCT v
        """

        try:
            cursor = self.db_connector.db.aql.execute(query)
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
        """
        Retrieves all inbound models to a given ending key.

        Args:
            - end_key (str): The key of the ending vertex.

        Returns:
            - list[ModelType] | None: List of inbound models or None if an error occurs.
        """

        vertex_type: str = self._get_collection_name_from_id(end_key)

        query: str = f"""
        FOR v, e, p IN 1..100 INBOUND '{vertex_type}/{end_key}' GRAPH '{self.default_graph_name}'
        RETURN DISTINCT v
        """

        try:
            cursor: Result[Cursor] = self.db_connector.db.aql.execute(query)
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

    def get_vertex_model_by_id(self, id: str) -> ModelType | None:
        """
        Retrieves a vertex model by its ID.

        Args:
            - id (str): The ID of the vertex.

        Returns:
            - ModelType | None: The vertex model or None if not found or an error occurs.
        """

        try:
            collection_name: str = self._get_collection_name_from_id(id)
            if collection_name == "unknown":
                logging.error(f"Unknown vertex type for ID: {id}")
                return None

            vertex_collection: StandardCollection = self.db_connector.db.collection(
                collection_name
            )
            vertex_result: Result[Json | None] = vertex_collection.get(id)

            if not vertex_result or not isinstance(vertex_result, dict):
                logging.error(
                    f"Vertex with ID {id} not found or is in an invalid format."
                )
                return None

            model_class: ModelType | None = self._get_model_class_from_collection_name(
                collection_name
            )
            if not model_class:
                logging.error(f"No model class found for collection: {collection_name}")
                return None

            return model_class(**vertex_result)  # type: ignore # FIXME: Fix type error

        except Exception as e:
            logging.error(f"Error in get_vertex_by_id: {e}")
            return None

    def _get_model_class_from_collection_name(
        self, collection_name: str
    ) -> ModelType | None:
        """
        Retrieves a vertex model by its ID.

        Args:
            - id (str): The ID of the vertex.

        Returns:
            - ModelType | None: The vertex model or None if not found or an error occurs.
        """

        model_class_map: dict = {
            "modules": ModuleModel,
            "classes": ClassModel,
            "functions": FunctionModel,
            "standalone_blocks": StandaloneCodeBlockModel,
            "directories": DirectoryModel,
        }
        return model_class_map.get(collection_name)

    def update_vertex_summary_by_id(self, id: str, new_summary: str) -> None:
        """
        Updates the summary of a vertex by its ID.

        Args:
            - id (str): The ID of the vertex.
            - new_summary (str): The new summary to be set.
        """

        try:
            collection_name: str = self._get_collection_name_from_id(id)
            if collection_name == "unknown":
                logging.error(f"Unknown vertex type for id: {id}")
                return

            vertex_collection: StandardCollection = self.db_connector.db.collection(
                collection_name
            )
            vertex_result: Result[Json | None] = vertex_collection.get(id)

            if not vertex_result:
                logging.error(f"Vertex with id {id} not found.")
                return

            if isinstance(vertex_result, dict):
                vertex = vertex_result
            else:
                logging.error("Retrieved vertex is not in a mutable format.")
                return None

            vertex["summary"] = new_summary

            vertex_collection.update(vertex)
            logging.info(f"Vertex with id {id} updated successfully.")

        except Exception as e:
            logging.error(f"Error in `update_vertex_by_id`: {e}")

    def get_all_modules(self) -> list[ModuleModel] | None:
        """
        Retrieves all modules from the graph.

        Returns:
            list[ModuleModel] | None: List of modules or None if an error occurs.
        """

        try:
            collection_name = "modules"
            module_collection: StandardCollection = self.db_connector.db.collection(
                collection_name
            )

            cursor: Result[Cursor] = module_collection.all()

            modules: list[ModuleModel] = []
            for doc in cursor:  # type: ignore # FIXME: Fix type error
                try:
                    module = ModuleModel(**doc)
                    modules.append(module)
                except Exception as e:
                    logging.error(f"Retrieved document is not in a valid format: {e}")
                    continue

            return modules

        except Exception as e:
            logging.error(f"Error in get_all_modules: {e}")
            return None

    def get_all_vertices(self) -> list[ModelType] | None:
        """
        Retrieves all vertices from the graph.

        Returns:
            list[ModelType] | None: List of vertices or None if an error occurs.
        """

        all_vertices: list[ModelType] = []
        vertex_collections: list[str] = (
            helper_functions.pluralized_and_lowered_block_types()
        )

        for collection_name in vertex_collections:
            try:
                collection: StandardCollection = self.db_connector.db.collection(
                    collection_name
                )
                cursor: Result[Cursor] = collection.all()

                for doc in cursor:  # type: ignore # FIXME: Fix type error
                    model_class: ModelType | None = (
                        self._get_model_class_from_collection_name(collection_name)
                    )
                    if model_class:
                        model: ModelType = model_class(**doc)  # type: ignore # FIXME: Fix type error
                        all_vertices.append(model)
                    else:
                        logging.warning(
                            f"No model class found for collection: {collection_name}"
                        )

            except Exception as e:
                logging.error(f"Error fetching vertices from {collection_name}: {e}")

        return all_vertices
