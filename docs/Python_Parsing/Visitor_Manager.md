# 👀 Fenec Visitor Manager

The Visitor Manager in Fenec is responsible for orchestrating the process of scanning, parsing, and modeling Python code within a specified directory structure. It works in conjunction with the Python Parser and Model Builders to create a comprehensive representation of the codebase.

## 🌟 Features

-   🗂️ Recursive directory scanning for Python files
-   🚫 Exclusion of specified directories (e.g., `.venv`, `node_modules`)
-   🏗️ Construction of module and directory models
-   🔄 Management of imports and dependencies across modules
-   🗺️ Creation of a directory-to-module mapping

> **NOTE:** The Visitor Manager is an internal component of Fenec used for code analysis and model construction. It is not meant for direct interaction by end-users. The documentation is provided for reference and internal development purposes and should be used for diagnosing issues, extending Fenec's functionality, or gaining a better understanding of how Fenec works.

## 🧩 Core Components

### VisitorManager

The main class responsible for managing the visiting process:

-   `__init__(self, directory: str)`: Initializes the manager with a root directory.
-   `process_files(self) -> VisitorManagerProcessFilesReturn`: Processes all Python files in the directory structure.

### ImportAndDependencyUpdater

A utility class for updating imports and dependencies across module models:

-   `update_imports(self) -> None`: Updates import statements across all module models.

### Key Helper Classes

-   `VisitorManagerProcessFilesReturn`: A dataclass representing the return value of `process_files()`.
-   `DirectoryDetails`: A dataclass representing details of a directory.

## 🚀 Usage

Here's a basic example of how to use the Visitor Manager:

```python
from fenec.python_parser.visitor_manager import VisitorManager

# Initialize the Visitor Manager with a directory path
manager = VisitorManager("/path/to/your/python/project")

# Process all Python files in the directory
result = manager.process_files()

# Access the processed models and directory structure
for model in result.models_tuple:
    print(f"Processed model: {model.id}")

for directory, modules in result.directory_modules.items():
    print(f"Directory: {directory}")
    for module in modules:
        print(f"  - Module: {module}")
```

## 🔄 Process Flow

1. **Directory Scanning**: The manager recursively scans the specified directory, identifying Python files while excluding specified directories.

2. **File Parsing**: Each identified Python file is parsed using the `PythonParser`.

3. **Model Building**: Module models are constructed for each parsed file.

4. **Import and Dependency Updating**: The `ImportAndDependencyUpdater` processes all module models to ensure consistent import and dependency information.

5. **Directory Model Creation**: Models for the directory structure are created, establishing relationships between directories and modules.

6. **Result Compilation**: All created models (modules and directories) are compiled into a single tuple, along with the directory-to-module mapping.

## 🚧 Under Development

The Visitor Manager in Fenec is under active development. Current areas of focus include:

-   Optimizing the scanning and processing of large codebases
-   Enhancing the handling of complex import scenarios
-   Improving the representation of project-wide dependencies

## 🔮 Future Enhancements

1. **Incremental Processing**: Implement the ability to process only changed files in subsequent runs.
2. **Parallel Processing**: Explore opportunities for concurrent file processing to improve performance.
3. **Custom Exclusion Rules**: Allow users to define custom rules for excluding directories or files.
4. **Integration with Version Control**: Incorporate version control information into the visiting process.

## 🤝 Contributing

We welcome contributions to improve and expand the Visitor Manager in Fenec! If you have ideas for enhancing the visiting process or improving code analysis, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Improving the efficiency of large-scale codebase processing
-   Enhancing the import and dependency resolution logic
-   Developing more sophisticated directory and module relationship models
-   Implementing support for additional Python project structures

## 🗺️ Roadmap

The future development of Fenec's Visitor Manager will focus on:

1. Enhancing scalability for very large Python projects
2. Improving the accuracy and comprehensiveness of import and dependency tracking
3. Developing more advanced code analysis features based on the visited structure
4. Exploring integration with other code analysis and visualization tools

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's Visitor Manager and look forward to your contributions in making it even more powerful and versatile!
