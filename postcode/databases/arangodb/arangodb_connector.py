import logging
from typing import Any
from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.result import Result
from arango.typings import Jsons, Json

import postcode.databases.arangodb.helper_functions as helper_functions

# from postcode.models import (
#     ModuleModel,
#     ClassModel,
#     FunctionModel,
#     StandaloneCodeBlockModel,
# )


# test = ArangoClient(hosts="http://localhost:8529")
class ArangoDBConnector:
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
        if not self.db.has_collection(collection_name):
            self.db.create_collection(collection_name, edge=True)
            logging.info(f"Created edge collection: {collection_name}")

    def delete_all_collections(self) -> None:
        collections: Result[Jsons] = self.db.collections()

        for collection in collections:  # type: ignore # FIXME: Fix type error
            if not collection["name"].startswith("_"):  # Skip system collections
                self.db.delete_collection(collection["name"])
                logging.info(f"Deleted collection: {collection['name']}")

    def ensure_collections(self) -> None:
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
