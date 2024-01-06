import logging
from typing import Any
from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.result import Result
from arango.typings import Jsons, Json

import postcode.databases.arangodb.helper_functions as helper_functions


class ArangoDBConnector:
    """
    A connector class for interacting with ArangoDB to manage collections and ensure proper database setup.

    This class provides methods to connect to an ArangoDB instance, create or ensure the existence of a specified database, collections, and edge collections. It also supports deletion of all user-defined collections within the database.

    Attributes:
        - client (ArangoClient): The ArangoDB client instance.
        - username (str): The username used for authentication.
        - password (str): The password used for authentication.
        - db_name (str): The name of the ArangoDB database.

    Example:
        ```python
        # This example demonstrates how to use ArangoDBConnector to connect to an ArangoDB instance and ensure collections.
        connector = ArangoDBConnector(url="http://localhost:8529", username="root", password="openSesame", db_name="postcode")
        connector.ensure_collections()
        ```

    Methods:
        - ensure_collections(): Ensures the existence of required collections and edge collections.
        - ensure_collection(collection_name, schema=None): Ensures the existence of a collection with an optional specified schema.
        - ensure_edge_collection(collection_name): Ensures the existence of an edge collection.
        - delete_all_collections(): Deletes all user-defined collections within the ArangoDB database.
    """

    def __init__(
        self,
        url: str = "http://localhost:8529",
        username: str = "root",
        password: str = "openSesame",
        db_name: str = "postcode",
    ) -> None:
        self.client = ArangoClient(hosts=url)
        self.username: str = username
        self.password: str = password
        self.db_name: str = db_name
        self.db: StandardDatabase = self._ensure_database()

    def _ensure_database(self) -> StandardDatabase:
        """
        Ensures the existence of the specified database, creating it if necessary.

        Returns:
            StandardDatabase: The ArangoDB database instance.
        """

        sys_db: StandardDatabase = self.client.db(
            "_system", username=self.username, password=self.password
        )
        if not sys_db.has_database(self.db_name):
            sys_db.create_database(self.db_name)
        return self.client.db(
            self.db_name, username=self.username, password=self.password
        )

    # def _ensure_vertex_collections(self, vertex_collections: list[str]) -> None:
    #     for collection in vertex_collections:
    #         if not self.db.has_collection(collection):
    #             self.db.create_collection(collection)

    def _get_current_schema(self, collection_name: str) -> dict:
        """
        Retrieves the current schema of a collection.

        Args:
            - collection_name (str): The name of the collection.

        Returns:
            dict: The current schema of the collection.
        """

        collection = self.db.collection(collection_name)
        try:
            properties: Result[Json] = collection.properties()
            return properties.get("schema", {})  # type: ignore # FIXME: Fix type error
        except Exception as e:
            logging.error(f"Error retrieving current schema for {collection_name}: {e}")
            return {}

    def ensure_collection(
        self, collection_name: str, schema: dict[str, Any] | None = None
    ) -> None:
        """
        Ensures the existence of a collection with an optional specified schema.

        Args:
            - collection_name (str): The name of the collection.
            - schema (dict[str, Any], optional): The schema to be applied to the collection. Defaults to None.
        """

        if not self.db.has_collection(collection_name) and not schema:
            self.db.create_collection(collection_name)
            logging.info(f"Created collection: {collection_name}")
        # else:
        #     current_schema = self._get_current_schema(collection_name)
        #     self.db.collection(collection_name)
        # if current_schema != schema:
        #     collection = self.db.collection(collection_name)
        #     try:
        #         collection.configure(schema=schema)
        #         logging.info(f"Updated schema for collection: {collection_name}")
        #     except Exception as e:
        #         logging.error(f"Error updating schema for {collection_name}: {e}")

    def ensure_edge_collection(self, collection_name: str) -> None:
        """
        Ensures the existence of an edge collection.

        Args:
            - collection_name (str): The name of the edge collection.
        """

        if not self.db.has_collection(collection_name):
            self.db.create_collection(collection_name, edge=True)
            logging.info(f"Created edge collection: {collection_name}")

    def delete_all_collections(self) -> None:
        """Deletes all user-defined collections within the ArangoDB database."""
        collections: Result[Jsons] = self.db.collections()

        for collection in collections:  # type: ignore # FIXME: Fix type error
            if not collection["name"].startswith("_"):  # Skip system collections
                self.db.delete_collection(collection["name"])
                logging.info(f"Deleted collection: {collection['name']}")

    def ensure_collections(self) -> None:
        """
        Ensures the existence of required collections and edge collections.

        This includes creating collections for modules, classes, functions, standalone code blocks, and the "code_edges" edge collection.
        """
        # model_schemas: dict[str, dict[str, Any]] = self._get_model_schemas()
        required_collections: list[
            str
        ] = helper_functions.pluralized_and_lowered_block_types()

        for collection_name in required_collections:
            # schema: dict[str, Any] = model_schemas[collection_name]
            # self.ensure_collection(collection_name, schema)
            self.ensure_collection(collection_name)

        self.ensure_edge_collection("code_edges")

    # def _get_model_schemas(self) -> dict[str, dict[str, Any]]:
    #     return {
    #         "modules": ModuleModel.model_json_schema(),
    #         "classes": ClassModel.model_json_schema(),
    #         "functions": FunctionModel.model_json_schema(),
    #         "standalone_blocks": StandaloneCodeBlockModel.model_json_schema(),
    #     }
