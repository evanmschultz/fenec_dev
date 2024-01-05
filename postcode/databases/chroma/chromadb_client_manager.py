import logging
from typing import Any, Sequence

import postcode.types.chroma as chroma_types


class ChromaClientHandler:
    """
    Class for managing a ChromaDB client.

    Provides functionality for managing a ChromaDB client, including creating, deleting, and listing collections.
    This class is part of the postcode library, offering default values and extended functionality.

    Attributes:
        client (chroma.ClientAPI): The ChromaDB client being managed.

    Methods:
        - `get_or_create_collection`: Gets or creates a ChromaDB collection with the given name.
        - `delete_collection`: Deletes a ChromaDB collection with the given name.
        - `list_collections`: Lists all ChromaDB collections.
        - `get_client_settings`: Gets the settings of the ChromaDB client.
        - `reset_client`: Resets the ChromaDB client to its initial state.

    Notes:
        Import defined in postcode.databases.chroma `__init__.py`. Import using:
            `from postcode.databases.chroma import ChromaDBClientManager`

    Examples:
        ```Python
        from postcode.databases.chroma import ChromaDBClientBuilder, ChromaDBClientManager

        # Create a persistent ChromaDB client
        client: chroma.ClientAPI = ChromaDBClientBuilder.create_persistent_client()

        # Create a ChromaDB client manager instance
        client_manager = ChromaDBClientManager(client)
        ```
    """

    def __init__(self, client: chroma_types.ClientAPI) -> None:
        self.client: chroma_types.ClientAPI = client

    def get_or_create_collection(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
        embedding_function: chroma_types.EmbeddingFunction[list[str]]
        | None = chroma_types.ef.DefaultEmbeddingFunction(),
    ) -> chroma_types.Collection:
        """
        Gets or creates a ChromaDB collection with the given name.

        Checks if the collection exists and returns it if it does. Otherwise, creates the collection and returns it.

        Args:
            - name (str): The name of the collection to get or create.
            - metadata (dict[str, Any]): The metadata for the collection.
            - embedding_function (chroma_types.EmbeddingFunction): The embedding function for the collection.

        Returns:
            - collection (chroma.Collection): The collection object with the given name. The collection object is a Pydantic Model
                with the following attributes:
                    - name: str
                    - id: UUID
                    - metadata: CollectionMetadata | None
                    - tenant: str | None
                    - database: str | None

        Notes:
            - This is done this way for logging purposes as opposed simply using chromadb's `get_or_create_collection` method
                directly.

        Examples:
            ```Python
            from postcode.databases.chroma import ChromaDBClientBuilder, ChromaDBClientManager
            import postcode.types.chromadb.types as chroma_types

            from example_module_with_manager_defined import client_manager

            # Create or get a collection using the client_manager instance
            collection: chroma_types.Collection = client_manager.get_or_create_collection("my_collection")
            ```
        """

        logging.info(f"Getting or creating collection: {name}")
        try:
            return self.client.get_or_create_collection(
                name,
                metadata=metadata,
                embedding_function=embedding_function,  # type: ignore # FIXME: Fix type error in chroma as it Images are not yet supported, and we won't use them
            )
        except Exception as e:
            raise ValueError(f"Error getting or creating ChromaDB collection: {e}")

    def delete_collection(self, name: str) -> None:
        """
        Deletes a ChromaDB collection with the given name.

        Args:
            - name (str): The name of the collection to delete.

        Raises:
            - ValueError: If the collection does not exist.

        Examples:
            ```Python
            client_manager.delete_collection("my_collection")
            ```
        """

        if self.client.get_collection(name):
            logging.info(f"Deleting collection {name}")
            self.client.delete_collection(name)
        else:
            raise ValueError(f"Collection {name} does not exist.")

    def list_collections(self) -> Sequence[chroma_types.Collection]:
        """
        Lists all ChromaDB collections.

        Returns:
            - client_list (Sequence[chroma.Collection]): A list of all ChromaDB collections A collection object is a Pydantic
                Model with the following attributes:
                    - name: str
                    - id: UUID
                    - metadata: CollectionMetadata | None
                    - tenant: str | None
                    - database: str | None

        Examples:
            ```Python
            collections_list: Sequence[chroma_types.Collection] = client_manager.list_collections()
            ```
        """

        return self.client.list_collections()

    def get_client_settings(self) -> chroma_types.Settings:
        """
        Gets the setting used to instantiate the ChromaDB client.

        Returns:
            - settings (chroma_types.Settings): The client settings as a settings object defined by ChromaDB.

        Examples:
            ```Python
            settings: chroma_types.Settings = client_manager.get_client_settings()
            ```
        """

        return self.client.get_settings()

    def reset_client(self) -> None:
        """
        Resets the ChromaDB client to its initial state.

        This method resets the client settings and clears any cached or temporary data. It iterates over the collections,
        logging their names, and then resets the client. If the reset operation is unsuccessful, it raises a ValueError.

        Raises:
            ValueError: If the client reset operation is unsuccessful.

        Notes:
            This method loops through the collections_list as opposed to immediately calling ChromaDB's
                `reset` method for logging purposes.

        Examples:
            ```Python
            client_manager.reset_client()  # Resets the client and logs the collections
            ```
        """
        reset_successful: bool = self.client.reset()
        if reset_successful:
            logging.info("Resetting client with:")

            if collections := self.list_collections():
                for collection in collections:
                    print(f"\t\t\t\tCollection: {collection.name}")
            else:
                print("\t\t\t\tNo collections.\n")

            logging.info("Client reset successful.")
        else:
            raise ValueError("Client reset unsuccessful.")
