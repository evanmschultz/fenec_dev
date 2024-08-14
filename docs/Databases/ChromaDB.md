# 🌈 Chroma Wrapper

The Chroma wrapper in Fenec provides a robust interface for interacting with ChromaDB, a vector database for storing and retrieving embeddings. This module simplifies the process of managing code summaries, their embeddings, and associated metadata within ChromaDB, as well as vector based search and retrieval.

## 🌟 Features

-   🔗 Connection and interaction with ChromaDB
-   📊 Creation and management of collections for code summaries
-   🔍 Efficient storage and retrieval of code summaries and their embeddings
-   🔄 CRUD operations for managing summaries and embeddings
-   🧠 Integration with AI services for generating embeddings
-   🔧 Utility functions for setting up and managing ChromaDB instances

> **NOTE:** This is an internal component of Fenec and is not intended for direct interaction by end-users. It is a critical part of Fenec's code analysis pipeline, enabling the storage and retrieval of code summaries and embeddings for further processing. The documentation is provided for reference and internal development purposes and should be used for diagnosing issues or extending Fenec's functionality, or simply gaining a better understanding of how Fenec works.

## 🧩 Components

### ChromaClientHandler

The `ChromaClientHandler` class serves as the primary interface for establishing and managing connections to ChromaDB.

#### Key Methods:

-   `get_or_create_collection`: Gets or creates a ChromaDB collection with the given name.
-   `delete_collection`: Deletes a ChromaDB collection with the given name.
-   `list_collections`: Lists all ChromaDB collections.
-   `get_client_settings`: Gets the settings of the ChromaDB client.
-   `reset_client`: Resets the ChromaDB client to its initial state.

### ChromaCollectionManager

The `ChromaCollectionManager` class provides high-level operations for managing code summaries within a specific ChromaDB collection.

#### Key Methods:

-   `collection_embedding_count`: Gets the total number of embeddings in the collection.
-   `add_embeddings`: Adds embeddings to the collection.
-   `get_embeddings`: Gets embeddings and their metadata from the collection.
-   `query_collection`: Queries and returns the `n` nearest neighbors from the collection.
-   `modify_collection_name`: Modifies the name of the collection.
-   `modify_collection_metadata`: Modifies the metadata of the collection.
-   `upsert_models`: Loads or updates the embeddings of the provided models into the collection.

### Utility Functions

The module also includes utility functions for setting up and managing ChromaDB instances:

-   `setup_chroma`: Sets up and returns a Chroma Collection Manager.
-   `setup_chroma_with_update`: Sets up Chroma with model updates and returns a Chroma Collection Manager.

## 🚀 Usage

Here's a basic example of how to use the Chroma functionality:

```python
from fenec.databases.chroma import setup_chroma, setup_chroma_with_update
from fenec.types.fenec import ModelType

# Set up a basic Chroma Collection Manager
collection_manager = setup_chroma("my_collection")

# Query the collection
results = collection_manager.query_collection(
    queries=["binary search"],
    n_results=5,
    where_filter={"block_type": "FUNCTION"},
    include_in_result=["metadatas", "documents", "distances"]
)

# Set up Chroma with model updates
models: list[ModelType] = [...]  # Your list of models
updated_collection_manager = setup_chroma_with_update(models, "updated_collection")

# Add new embeddings
ids = ["id1", "id2"]
documents = ["document1", "document2"]
metadatas = [{"key1": "value1"}, {"key2": "value2"}]
updated_collection_manager.add_embeddings(ids, documents, metadatas)
```

## 🚧 Under Development

Please note that the Chroma functionality, like the rest of Fenec, is under active development and subject to change. Current areas of focus include:

-   Optimizing embedding generation and storage for large codebases
-   Enhancing query capabilities for more precise code search
-   Improving integration with other components of Fenec
-   Expanding support for different embedding models and techniques

## 🤝 Contributing

We welcome contributions to improve and expand the Chroma functionality! If you have ideas or want to contribute, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests, tests, and more tests! - Due to a rush to get Fenec out the door, we have a lot of untested code.
-   Implementing support for additional embedding models
-   Optimizing query performance for large collections
-   Developing utilities for managing and analyzing stored embeddings
-   Enhancing the integration between Chroma and other Fenec components

## 🗺️ Roadmap

The future development of the Chroma functionality will focus on:

1. Implementing more sophisticated querying capabilities for complex code search
2. Enhancing performance and storage efficiency for large-scale projects
3. Developing tools for visualizing and analyzing code relationships based on embeddings
4. Expanding integration with AI services for more advanced code understanding

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's Chroma functionality and look forward to your contributions in making it even more powerful and user-friendly!
