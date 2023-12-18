import logging
from typing import Any, Mapping

import postcode.types.chroma as chroma_types
from postcode.types.postcode import ModelType, ModuleModel


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
        - `upsert_models`: Loads or updates the embeddings of the provided module models into the collection.

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

        if not len(ids) == len(documents) == len(metadatas):
            raise ValueError("The length of ids, documents, and metadatas must match.")

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
                return results
            else:
                logging.warning(
                    f"No results found from collection {self.collection.name}."
                )

        except Exception as exception:
            raise exception

    def modify_collection_name(self, name: str) -> None:
        """
        Modifies the name of the collection managed by this class.

        Args:
            - name (str): The new name to assign to the collection.

        Examples:
            ```Python
            # Rename the collection to 'new_collection_name'
            collection_manager.modify_collection_name('new_collection_name')
            ```
        """

        self.collection.modify(name=name)

    def modify_collection_metadata(
        self, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Modifies the metadata of the collection managed by this class.

        Args:
            - metadata (dict[str, Any] | None): The new metadata to assign to the collection. If None, no change is made.

        Examples:
            ```Python
            # Update metadata of the collection
            new_metadata = {"description": "Updated collection metadata"}
            collection_manager.modify_collection_metadata(new_metadata)
            ```
        """

        self.collection.modify(metadata=metadata)

    def _update_metadata_or_documents_by_ids(
        self,
        ids: list[str],
        metadatas: list[Mapping[str, str | int | float | bool]] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        """
        Updates the metadata or documents of specific entries in the collection by their ids.

        Args:
            - ids (list[str]): List of ids of the entries to be updated.
            - metadatas (list[Mapping[str, Any]] | None): List of metadata updates corresponding to the ids.
            - documents (list[str] | None): List of document updates corresponding to the ids.

        Raises:
            - ValueError: If neither metadatas nor documents are provided.
            - ValueError: If the length of ids and documents don't match.
            - ValueError: If the length of ids and metadatas don't match.
            - ValueError: If the length of ids, metadatas, and documents don't match.

        Notes:
            - As of now, ChromaDB doesn't raise an exception if you provide an id that doesn't exist.

        Examples:
            ```Python
            # Update metadata and documents for specific ids
            ids_to_update = ['id1', 'id2']
            metadata_updates = [{"key1": "value1"}, {"key2": "value2"}]
            document_updates = ["new document 1", "new document 2"]
            collection_manager.update_metadata_or_documents_by_ids(ids_to_update, metadata_updates, document_updates)
            ```
        """

        if not metadatas and not documents:
            raise ValueError("You must provide either metadatas or documents.")
        if not metadatas and documents:
            if len(ids) != len(documents):
                raise ValueError("The length of ids and documents must match.")
        if metadatas and not documents:
            if len(ids) != len(metadatas):
                raise ValueError("The length of ids and metadatas must match.")
        if metadatas and documents:
            if len(ids) != len(metadatas) != len(documents):
                raise ValueError(
                    "The length of ids, metadatas, and documents must match."
                )
        for index, id in enumerate(ids):
            if not self.collection.get(id):
                logging.error(
                    f"Id {id} does not exist in collection {self.collection.name}."
                )
                ids.pop(index)
                if metadatas:
                    popped_metadata = metadatas.pop(index)
                    if popped_metadata:
                        logging.warning(
                            f"Removing metadata at index {index} from update."
                        )
                if documents:
                    popped_document = documents.pop(index)
                    if popped_document:
                        logging.warning(
                            f"Removing document at index {index} from update."
                        )

        if not ids:
            logging.warning("All updates failed.")
            return None
        else:
            logging.info(f"Updating collection {self.collection.name} with ids {ids}.")
            self.collection.update(ids=ids, metadatas=metadatas, documents=documents)

    def _upsert_documents(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[Mapping[str, str | int | float | bool]],
        # embeddings: list[chroma_types.Embedding],
    ) -> None:
        """
        Inserts or updates documents in the collection, based on the provided ids.

        Args:
            - ids (list[str]): List of ids for the documents to be inserted or updated.
            - documents (list[str]): List of documents corresponding to the ids.
            - metadatas (list[Mapping[str, Any]]): List of metadata corresponding to the ids.

        Raises:
            - ValueError: If the lengths of ids, documents, and metadatas don't match.

        Examples:
            ```Python
            # Upsert documents in the collection
            ids = ['id1', 'id2']
            documents = ['doc1', 'doc2']
            metadatas = [{"meta1": "value1"}, {"meta2": "value2"}]

            # Upsert documents in the collection
            collection_manager.upsert_documents(ids, documents, metadatas)
            ```
        """

        if len(ids) != len(documents) != len(metadatas):
            raise ValueError("The length of ids, documents, and metadatas must match.")

        logging.info(f"Upserting collection {self.collection.name} with ids {ids}.")
        self.collection.upsert(
            ids=ids,
            # embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def delete_embeddings(self, ids: list[str]) -> None:
        """
        Deletes embeddings from the collection based on the provided ids.

        Args:
            - ids (list[str]): List of ids corresponding to the embeddings to be deleted.

        Examples:
            ```Python
            # Delete specific embeddings by ids
            ids_to_delete = ['id1', 'id2']
            collection_manager.delete_embeddings(ids_to_delete)
            ```
        """

        ids_to_delete: list[str] = ids.copy()
        for index, id in enumerate(ids_to_delete):
            if not self.collection.get(id):
                logging.error(
                    f"Id {id} does not exist in collection {self.collection.name}."
                )
                ids_to_delete.pop(index)

        if not ids_to_delete:
            logging.warning("No IDs given were in the database.")
            return None

        logging.info(
            f"Deleting embeddings from collection {self.collection.name} with ids {ids_to_delete}."
        )
        self.collection.delete(ids_to_delete)

    def upsert_models(self, module_models: tuple[ModuleModel, ...]) -> None:
        """
        Loads or updates the embeddings of the provided module models into the collection.

        The Pydantic models are converted to a dictionary with a format that ChromaDB can use, then the ids, documents, and metadatas
        are added to their respective lists. The lists are then either added to or updated in the collection depending on whether or
        not the code blocks were in the the collection to begin with.

        Args:
            - module_models (tuple[ModuleModel, ...]): The module models to load or update into the collection.

        Examples:
            ```Python
            # Upsert module models into the collection
            module_models = (module_model1, module_model2)
            collection_manager.upsert_models(module_models)
            ```
        """

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[Mapping[str, str | int | float | bool]] = []

        for module_model in module_models:
            if module_model.summary:
                ids.append(module_model.id)
                documents.append(module_model.summary)
                metadatas.append(module_model.convert_to_metadata())

            if module_model.children:
                for child in module_model.children:
                    child_data: dict[str, Any] = self._recursively_gather_child_data(
                        child
                    )
                    ids.extend(child_data["ids"])
                    documents.extend(child_data["documents"])
                    metadatas.extend(child_data["metadatas"])

        logging.info(
            f"{self.collection.name} has {self.collection_embedding_count()} embeddings."
        )
        self._upsert_documents(ids=ids, documents=documents, metadatas=metadatas)
        logging.info(
            f"After upsert {self.collection.name} has {self.collection_embedding_count()} embeddings."
        )

    def _recursively_gather_child_data(self, model: ModelType) -> dict[str, Any]:
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[Mapping[str, str | int | float | bool]] = []
        if model.summary:
            ids.append(model.id)
            documents.append(model.summary)
            metadatas.append(model.convert_to_metadata())
        else:
            logging.warning(f"Child {model.id} has no summary.")
        if model.children:
            for child in model.children:
                child_data: dict[str, Any] = self._recursively_gather_child_data(child)
                ids.extend(child_data["ids"])
                documents.extend(child_data["documents"])
                metadatas.extend(child_data["metadatas"])

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }
