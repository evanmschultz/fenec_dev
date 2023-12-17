import logging
from typing import Any, Mapping, Sequence

import postcode.types.chroma as chroma_types


class ChromaDBCollectionManager:
    """
    Manages a collection within ChromaDB instance, providing functionalities for adding, retrieving,
    and querying embeddings, and their associated metadata.

    This class serves as an interface to interact with a specific collection in ChromaDB.

    Attributes:
        - collection (chroma_types.Collection): An instance of the Collection class from ChromaDB
            which this manager is responsible for.

    Methods:
        - `collection_embedding_count`: Gets the total number of embeddings in the collection.
        - `add_embeddings`: Adds embeddings to the collection.
        - `get_embeddings`: Gets embeddings and their metadata from the collection in the form of a TypedDict.
        - `query_collection`: Queries and returns the `n` nearest neighbors from the collection.

    Examples:
        ```Python
        from postcode.databases.chroma import ChromaDBClientBuilder
        import postcode.types.chromadb.types as chroma_types

        # Create a persistent ChromaDB client
        client: chroma_types.ClientAPI = ChromaDBClientBuilder.create_persistent_client()

        # Instantiate the ChromaDBCollectionManager with a specific collection
        collection_manager: ChromaDBCollectionManager = (
            ChromaDBCollectionManager(client.get_collection("my_collection"))
        )

        # Example usage of the collection manager
        embedding_count: int = collection_manager.collection_embedding_count()
        print(f"Total embeddings: {embedding_count}")
        ```
    """

    def __init__(self, collection: chroma_types.Collection) -> None:
        self.collection: chroma_types.Collection = collection

    def collection_embedding_count(self) -> int:
        """
        Gets the total number of embeddings in the collection.

        Returns:
            - embedding_count (int): The total number of embeddings in the collection.

        Examples:
            ```Python
            embedding_count: int = collection_manager.get_collection_embedding_count()
            ```
        """

        embedding_count: int = self.collection.count()
        logging.info(
            f"Collection {self.collection.name} has {embedding_count} embeddings."
        )

        return embedding_count

    def add_embeddings(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[Mapping[str, str | int | float | bool]],
    ) -> None:
        """
        Adds embeddings to the collection.

        Args:
            - ids (list[str]): A list of ids to add to the collection.
            - documents (list[str]): A list of documents to add to the collection.
            - metadatas (list[dict[str, Any]]): A list of metadatas to add to the collection.

        Raises:
            - ValueError - If you don't provide either embeddings or documents.
            - ValueError: If the length of ids, embeddings, metadatas, or documents don't match.
            - ValueError - If you provide an id that already exists.

        Examples:
            ```Python
            # define the ids, metadatas, and documents to add to the collection
            id: list[str] = ["my_id", "my_id2"]
            metadatas: list[dict[str, Any]] = [
                {"my_metadata": "my_metadata_value"},
                {"my_metadata2": "my_metadata_value2"},
            ]
            documents: list[str] = ["my_document", "my_document2"]

            # add the embeddings to the collection
            collection_manager.add_embeddings(id, metadatas, documents)
            ```
        """

        try:
            logging.info(f"Adding embeddings to collection {self.collection.name}")
            self.collection.add(ids, documents=documents, metadatas=metadatas)
        except Exception as exception:
            raise exception

    def get_embeddings(
        self,
        ids: list[str] | None,
        *,
        where_filter: chroma_types.Where | None = None,
        limit: int | None = None,
        where_document_filter: chroma_types.WhereDocument | None = None,
        include_in_result: chroma_types.Include = ["metadatas", "documents"],
    ) -> chroma_types.GetResult | None:
        """
        Gets embeddings and their metadata from the collection in the form of a TypedDict.

        Args:
            - ids (list[str]): A list of ids to get from the collection.
            - where_filter (chroma_types.Where | None): A TypedDict used to filter the results.
            - limit (int | None): The maximum number of results to return.
            - where_document_filter (chroma_types.WhereDocument | None): A TypedDict used to filter the results by the document,
                e.g. `{$contains: {"text": "hello"}}`
            - include_in_result (chroma_types.Include | None): A list used of what to return from the results, e.g. `["metadatas", "embeddings", "documents"]`

        Returns:
            - embeddings (TypedDict): A typed dict of embedding data from the collection with the following keys:
                - ids: list[str]
                - embeddings: list[Embedding] | None
                - documents: list[str] | None
                - uris: chroma_types.URIs | None
                - data: chroma_types.Loadable | None
                - metadatas: list[chroma_types.Metadata]]

        Raises:
            - ValueError: If the length of ids, embeddings, metadatas, or documents don't match.
            - ValueError: If you provide an id that doesn't exist.

        Examples:
            ```Python
            import postcode.types.chromadb.types as chroma_types

            # define the ids, filters to use to get embeddings from the collection
            ids: list[str] = ["my_id", "my_id2"]
            where_filter: chroma_types.Where = {"my_metadata": "my_metadata_value"}
            where_document_filter: chroma_types.WhereDocument = {"$contains": {"text": "hello"}}

            # define the data to return from the collection
            include_in_result: chroma_types.Include = ["metadatas"]

            # get the embeddings from the collection
            embeddings: chroma_types.GetResult = collection_manager.get_embeddings(
                ids,
                where_filter=where_filter,
                where_document_filter=where_document_filter,
                include_in_result=include_in_result
                )
            ```
        """

        try:
            logging.info(f"Getting embeddings from collection {self.collection.name}")
            return self.collection.get(
                ids,
                where=where_filter,
                limit=limit,
                where_document=where_document_filter,
                include=include_in_result,
            )
        except Exception as exception:
            raise exception

    def query_collection(
        self,
        queries: list[str],
        n_results: int = 10,
        where_filter: chroma_types.Where | None = None,
        where_document_filter: chroma_types.WhereDocument | None = None,
        include_in_result: chroma_types.Include = ["metadatas", "documents"],
    ) -> chroma_types.QueryResult | None:
        """
        Queries and returns the `n` nearest neighbors from the collection.

        Args:
            - queries (list[str]): A list of queries to search the collection for.
            - n_results (int): The number of results to return.
            - where_filter (chroma_types.Where | None): A TypedDict used to filter the results.
                - e.g. `{"block_type": "FUNCTION", "children": None}`
            - where_document_filter (chroma_types.WhereDocument | None): A TypedDict used to filter the results by the document,
                - e.g. `{$contains: "binary search"}`
            - include_in_result (chroma_types.Include | None): A list used of what to return from the results, e.g. `["metadatas", "embeddings", "documents"]`

        Returns:
            - results (chroma_types.QueryResult | None): A typed dict of query results from the collection, can have the following keys based on the
                `include_in_result` parameter:
                - ids: list[str] # The ids are always returned.
                - embeddings: List[list[Embedding]] | None
                - documents: list[list[str]]] | None
                - uris: list[list[URI]]] | None
                - data: list[Loadable] | None
                - metadatas: list[list[Metadata]] | None
                - distances: list[list[float]] | None

        Raises:
            - ValueError: If you don't provide query_texts.

        Examples:
            ```Python
            import postcode.types.chromadb.types as chroma

            # define the queries and filters used to search the collection
            queries: list[str] = ["binary search", "linear search"]
            where_filter: chroma_types.Where = {"block_type": "FUNCTION"}

            # define the data to return from the collection
            include_in_result: chroma_types.Include = ["metadatas", "documents", "distances"]

            # query the collection and return the results from the collection
            results: chroma_types.QueryResult = collection_manager.query_collection(
                queries,
                where_filter=where_filter,
                include_in_result=include_in_result
                )
            ```
        """
        try:
            logging.info(f"Querying collection {self.collection.name}")

            if results := self.collection.query(
                query_texts=queries,
                n_results=n_results,
                where=where_filter,
                where_document=where_document_filter,
                include=include_in_result,
            ):
                logging.info(
                    f"Got {len(results)} results from collection {self.collection.name}."
                )
                return results
            else:
                logging.warning(
                    f"No results found from collection {self.collection.name}."
                )

        except Exception as exception:
            raise exception

    def modify_collection_name(self, name: str) -> None:
        # TODO: Add docstring
        self.collection.modify(name=name)

    def modify_collection_metadata(
        self, metadata: dict[str, Any] | None = None
    ) -> None:
        # TODO: Add docstring
        self.collection.modify(metadata=metadata)

    def update_metadata_or_documents_by_ids(
        self,
        ids: list[str],
        metadatas: list[Mapping[str, str | int | float | bool]],
        documents: list[str],
    ) -> None:
        # TODO: Add docstring
        # TODO: Finish logic
        self.collection.update(ids=ids, metadatas=metadatas, documents=documents)
