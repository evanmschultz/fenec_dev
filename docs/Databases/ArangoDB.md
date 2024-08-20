# 🗄️ ArangoDB Wrapper

The ArangoDB wrapper in Fenec provides a powerful interface for interacting with ArangoDB, a graph database. This wrapper simplifies the process of storing, retrieving, and managing code structure data within ArangoDB, as well as constructing graph representations from ChromaDB collections.

## 🌟 Features

-   🔗 Connection and interaction with ArangoDB
-   📊 Creation and management of collections for different code elements
-   🕸️ Graph-based representation of code structures
-   👀 Visualization of code structures using ArangoDB's built-in visualization tools
-   🔄 CRUD operations for vertices (code elements) and edges (relationships)
-   🔍 Querying capabilities for code analysis (though not yet utilized fully in Fenec)
-   🔀 Construction of ArangoDB graphs from ChromaDB collections

> **⚠️ Note:** The ArangoDB wrapper is designed to be used internally by Fenec and is not intended for direct interaction by end-users. It is an essential component of Fenec's code analysis pipeline, enabling the storage and retrieval of code structures for further processing.

## 🧩 Components

### ArangoDBConnector

The `ArangoDBConnector` class serves as the primary interface for establishing and managing connections to ArangoDB.

#### Key Methods:

-   `ensure_collections()`: Creates necessary collections for storing code elements.
-   `ensure_collection(collection_name, schema=None)`: Ensures a specific collection exists.
-   `ensure_edge_collection(collection_name)`: Creates an edge collection for representing relationships.
-   `delete_all_collections()`: Removes all user-defined collections from the database.

### ArangoDBManager

The `ArangoDBManager` class provides high-level operations for managing code structures within ArangoDB.

#### Key Methods:

-   `upsert_models(module_models)`: Inserts or updates a list of code models in the database.
-   `process_imports_and_dependencies()`: Analyzes and creates edges for imports and dependencies.
-   `get_outbound_models(start_key)`: Retrieves all models connected outbound from a given key.
-   `get_inbound_models(end_key)`: Retrieves all models connected inbound to a given key.
-   `get_vertex_model_by_id(id)`: Fetches a specific model by its ID.
-   `update_vertex_summary_by_id(id, new_summary)`: Updates the summary of a specific model.
-   `get_all_modules()`: Retrieves all module models from the database.
-   `get_all_vertices()`: Fetches all vertices (code elements) from the database.
-   `construct_graph_from_chromadb(chroma_manager)`: Constructs an ArangoDB graph from a ChromaDB collection.

## 🚀 Usage

Here's a basic example of how to use the ArangoDB wrapper:

> **NOTE:** This is automatically handled by the Fenec API, so you don't need to interact with the ArangoDB wrapper directly unless you want to perform custom operations for testing, learning about how Fenec works, or extending Fenec's functionality.

```python
from fenec.databases.arangodb import ArangoDBConnector
from fenec.databases.arangodb import ArangoDBManager
from fenec.databases.chroma import ChromaCollectionManager

# Initialize the connector
connector = ArangoDBConnector(url="http://localhost:8529", username="root", password="openSesame", db_name="fenec")

# Create the manager
manager = ArangoDBManager(db_connector=connector)

# Ensure collections are set up
connector.ensure_collections()

# Upsert models (assuming you have a list of models)
manager.upsert_models(models)

# Process imports and dependencies
manager.process_imports_and_dependencies()

# Retrieve all modules
modules = manager.get_all_modules()

# Get outbound models for a specific module
outbound_models = manager.get_outbound_models("module_1__*__MODULE")

# Construct graph from ChromaDB
chroma_manager = ChromaCollectionManager(...)  # Initialize your ChromaDB manager
manager.construct_graph_from_chromadb(chroma_manager)
```

## 🔀 Constructing Graphs from ChromaDB

The `construct_graph_from_chromadb` method allows you to build an ArangoDB graph representation of your code structure based on data stored in ChromaDB. This is particularly useful when you want to transition from a vector-based representation to a graph-based one for more complex querying and analysis.

Here's how it works:

1. It retrieves all documents from the ChromaDB collection.
2. For each document, it extracts the metadata and summary.
3. Based on the `block_type` in the metadata, it determines the appropriate model class (e.g., ModuleModel, ClassModel, etc.).
4. It creates model instances using the `build_from_metadata` method of each model class.
5. The created models are then upserted into ArangoDB.
6. Finally, it processes imports and dependencies to create edges in the graph.

This process allows for a seamless transition between the vector database (ChromaDB) and the graph database (ArangoDB), enabling more sophisticated code analysis and querying capabilities.

### Constructing Graphs Programmatically (API)

You can construct the graph programmatically using the Fenec API:

```python
from fenec import Fenec
from pathlib import Path

# Initialize Fenec
fenec = Fenec(path=Path("/path/to/your/project"))

# Connect to the existing vectorstore
fenec.connect_to_vectorstore()

# Construct the graph from ChromaDB
fenec.construct_graph_from_chromadb(force=True)
```

### Constructing Graphs via CLI

You can also construct the graph using the Fenec CLI:

```bash
fenec --construct-graph # Assuming your project is already loaded, e.g. you just git cloned the Fenec repo
```

This command will connect to the existing vectorstore and construct the graph from the ChromaDB data.

> **⚠️ Important Note:** When you clone the Fenec project or share vectorstored information between collaborators, the graph will not be automatically constructed on your machine. This is because the ArangoDB graph is not easily transferrable. If you wish to use the visualization tools in ArangoDB or wish to update the project summaries, you'll need to explicitly construct the graph using one of the methods above.

> **💡 Tip for Collaboration:** When collaborating on projects using Fenec, it's recommended to share the ChromaDB vectorstore data. Each collaborator can then construct their own local graph as needed using the shared vectorstore information.
>
> It is wise to share the output_json, as well, as it has commit information for partial updates (though this is hardly ready to be used even in development as it can't work with multiple branches and should be setup as a github action/workflow).

## 🚧 Under Development

Please note that the ArangoDB wrapper, like the rest of Fenec, is under active development and subject to change. Current areas of focus include:

-   Optimizing graph queries for large codebases
-   Enhancing support for complex code relationships
-   Improving error handling and logging
-   Expanding the API to support more advanced code analysis tasks
-   Refining the process of constructing graphs from ChromaDB data

## 🤝 Contributing

We welcome contributions to improve and expand the ArangoDB wrapper functionality! If you have ideas or want to contribute, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests, tests, tests, tests, tests! - Due to a rush to get Fenec out the door, we have a lot of untested code.
-   Implementing advanced graph traversal algorithms
-   Optimizing database operations for large-scale projects
-   Enhancing the schema design for different code elements
-   Developing utilities for database maintenance and optimization
-   Improving the efficiency and robustness of the ChromaDB to ArangoDB graph construction process

## 🗺️ Roadmap

The future development of the ArangoDB wrapper will focus on:

1. Implementing more sophisticated querying capabilities for complex code analysis
2. Enhancing performance for large-scale codebases
3. Expanding integration with other components of Fenec
4. Refining the synchronization between ChromaDB and ArangoDB representations

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's ArangoDB wrapper and look forward to your contributions in making it even more powerful and user-friendly!
