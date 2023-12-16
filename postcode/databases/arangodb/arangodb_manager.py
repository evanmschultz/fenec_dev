from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.result import Result
from arango.typings import Jsons


class ArangoDBManager:
    def __init__(
        self,
        url: str = "http://localhost:8529",
        username: str = "root",
        password: str = "openSesame",
        db_name: str = "post_code",
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

    def _ensure_vertex_collections(self, vertex_collections: list[str]) -> None:
        for collection in vertex_collections:
            if not self.db.has_collection(collection):
                self.db.create_collection(collection)

    def ensure_collection(self, collection_name: str) -> None:
        if not self.db.has_collection(collection_name):
            self.db.create_collection(collection_name)
            print(f"Created collection: {collection_name}")

    def ensure_edge_collection(self, collection_name: str) -> None:
        if not self.db.has_collection(collection_name):
            self.db.create_collection(collection_name, edge=True)
            print(f"Created edge collection: {collection_name}")

    def delete_all_collections(self) -> None:
        collections: Result[Jsons] = self.db.collections()

        for collection in collections:  # type: ignore # FIXME: Fix type error
            if not collection["name"].startswith("_"):  # Skip system collections
                self.db.delete_collection(collection["name"])
                print(f"Deleted collection: {collection['name']}")

    def setup_collections(self):
        required_collections = [
            "modules",
            "classes",
            "functions",
            "standalone_blocks",
        ]
        for collection_name in required_collections:
            self.ensure_collection(collection_name)

        self.ensure_edge_collection("code_edges")


if __name__ == "__main__":
    # # Usage example
    # db_manager = ArangoDBManager()
    # db_manager.delete_all_collections()
    # db_manager.process_graph_data(
    #     "/Users/evanschultz/Documents/Code/post-code/output/json/"
    # )
    # db_manager.process_dependencies_and_imports()
    ...
