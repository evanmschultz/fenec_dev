# ⬆️ Updaters

## 🔍 Overview

The Fenec Updater system is a crucial component responsible for managing and updating the codebase representations within Fenec. It handles the process of detecting changes, updating models, and maintaining the consistency of various databases used by Fenec.

## 🧩 Core Components

### GraphDBUpdater

The main class responsible for orchestrating the update process, leveraging a graph database for accurate updates.

Key features:

-   Supports multi-pass summarization
-   Can update all models or only changed files
-   Integrates with Git for change detection
-   Manages interactions with ArangoDB and ChromaDB

### ChangeDetector

Responsible for identifying which models are affected by changes in the codebase.

Key features:

-   Detects directly changed models
-   Identifies connected models that may be affected by changes
-   Supports both unidirectional and bidirectional dependency analysis

### GitUpdater

Provides utilities for interacting with Git to detect changes in the codebase.

Key features:

-   Retrieves lists of changed files since the last update
-   Fetches the current commit hash

## 🚀 Update Process Flow

1. **Initialization**: A `GraphDBUpdater` is created with necessary configurations.
2. **Change Detection**:
    - For partial updates, changed files are identified using Git.
    - For full updates, all files are considered changed.
3. **File Parsing**: The codebase is parsed to create or update model representations.
4. **Affected Model Identification**: The `ChangeDetector` determines which models need updating.
5. **Database Updates**:
    - ArangoDB is updated with new or modified model information.
    - ChromaDB is updated for efficient retrieval of summaries.
6. **Summarization**: Affected models are summarized, potentially using multi-pass techniques.
7. **Final Updates**: Databases are updated with the new summaries and model information.

## 🔧 Key Functions

### GraphDBUpdater

-   `update_changed`: Updates only the changed files and their connected code blocks.
-   `update_all`: Performs a full update of all models in the project.
-   `_visit_and_parse_files`: Parses the codebase to create model representations.
-   `_upsert_models_to_graph_db`: Updates the graph database with new or modified models.
-   `_map_and_summarize_models`: Manages the summarization process for models.

### ChangeDetector

-   `get_affected_models`: Identifies models affected by changes in specified files.
-   `_get_connected_models`: Finds models connected to a given model in the dependency graph.

### GitUpdater

-   `get_changed_files_since_last_update`: Retrieves a list of changed Python files since a specified commit.
-   `get_current_commit_hash`: Fetches the hash of the current Git commit.

## 🔄 Multi-Pass Summarization

The updater system supports multi-pass summarization, allowing for more comprehensive and context-aware summaries:

1. **Single Pass**: Only directly affected models are summarized.
2. **Triple Pass**:
    - First pass: Summarize directly affected models.
    - Second pass: Summarize models depending on affected models.
    - Third pass: Re-summarize affected models with updated context.

## 🗃️ Database Interactions

-   **ArangoDB**: Used for storing the graph structure of the codebase, including dependencies between models.
-   **ChromaDB**: Utilized for efficient storage and retrieval of model summaries.

## 🚧 Current Limitations and Future Enhancements

1. **Scalability**: The current implementation may face challenges with very large codebases.
2. **Incremental Updates**: While changed file detection is supported, the summarization process could be further optimized for incremental updates.
3. **Conflict Resolution**: Handling conflicts in concurrent updates could be improved.

## 🤝 Contributing to Fenec Updaters

While the updater system is internal, contributions to improve its functionality are welcome. Areas for potential enhancement include:

-   Optimizing the change detection and affected model identification processes
-   Improving the efficiency of multi-pass summarization
-   Enhancing the integration with version control systems beyond Git

Please refer to the main Fenec [Contributing Guidelines](../../CONTRIBUTING.md) for more information on how to contribute to the project.

## 📚 Related Components

-   **Visitor System**: Works in tandem with updaters to parse and analyze code structures.
-   **AI Services**: Provide summarization capabilities used in the update process.
-   **Database Managers**: Handle the low-level interactions with ArangoDB and ChromaDB.

For a comprehensive understanding of Fenec's architecture, please refer to the main [Fenec Documentation](../../README.md).
