# 🗄️ ArangoDB Wrapper

The ArangoDB wrapper in Fenec provides a powerful interface for interacting with ArangoDB, a multi-model database. This wrapper simplifies the process of storing, retrieving, and managing code structure data within ArangoDB.

## 🌟 Features

-   🔗 Connection and interaction with ArangoDB
-   📊 Creation and management of collections for different code elements
-   🕸️ Graph-based representation of code structures
-   🔄 CRUD operations for vertices (code elements) and edges (relationships)
-   🔍 Querying capabilities for code analysis

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

## 🚀 Usage

Here's a basic example of how to use the ArangoDB wrapper:

> **NOTE:** This is automatically handled by the Fenec API, so you don't need to interact with the ArangoDB wrapper directly unless you want to perform custom operations for testing, learning about how Fenec works, or extending Fenec's functionality.

```python
from fenec.databases.arangodb import ArangoDBConnector
from fenec.databases.arangodb import ArangoDBManager

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
```

## 🚧 Under Development

Please note that the ArangoDB wrapper, like the rest of Fenec, is under active development and subject to change. Current areas of focus include:

-   Optimizing graph queries for large codebases
-   Enhancing support for complex code relationships
-   Improving error handling and logging
-   Expanding the API to support more advanced code analysis tasks

## 🤝 Contributing

We welcome contributions to improve and expand the ArangoDB wrapper functionality! If you have ideas or want to contribute, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests, tests, tests, tests, tests! - Due to a rush to get Fenec out the door, we have a lot of untested code.
-   Implementing advanced graph traversal algorithms
-   Optimizing database operations for large-scale projects
-   Enhancing the schema design for different code elements
-   Developing utilities for database maintenance and optimization

## 🗺️ Roadmap

The future development of the ArangoDB wrapper will focus on:

1. Implementing more sophisticated querying capabilities for complex code analysis
2. Enhancing performance for large-scale codebases
3. Developing tools for visualizing code structures stored in ArangoDB
4. Expanding integration with other components of Fenec

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's ArangoDB wrapper and look forward to your contributions in making it even more powerful and user-friendly!
