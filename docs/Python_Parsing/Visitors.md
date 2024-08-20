# 🕵🏻‍♀️ Visitors

## 🔍 Overview

The Fenec Visitor system is a crucial internal component responsible for traversing and analyzing Python code structures. It utilizes the `libcst` library to parse and process Python source code, building comprehensive models of code elements such as modules, classes, functions, and standalone blocks.

> **NOTE:** The Fenec Visitor system is an internal component and is not intended for direct use by end-users. This documentation is provided for reference, internal development purposes, and to aid in understanding Fenec's internal workings.

## 🧩 Core Components

### BaseVisitor

The foundation of Fenec's visitor system, `BaseVisitor` extends `libcst.CSTVisitor` and provides common functionality for all specific visitors.

Key features:

-   Maintains a stack of model builders
-   Processes comments and extracts position data from nodes

### ModuleVisitor

Extends `BaseVisitor` to specifically handle Python module structures.

Key responsibilities:

-   Processes module-level components (docstrings, imports, etc.)
-   Manages the creation and population of various code block models (classes, functions, standalone blocks)
-   Coordinates the dependency gathering process

## 🚀 Visitor Process Flow

1. **Initialization**: A `ModuleVisitor` is created with a `ModuleModelBuilder`.
2. **Tree Traversal**: The visitor walks through the CST (Concrete Syntax Tree) of the Python module.
3. **Node Processing**:
    - Module components are processed (imports, docstrings, etc.)
    - Class and function definitions trigger the creation of respective model builders
    - Standalone code blocks are identified and processed
4. **Model Building**: As nodes are visited, corresponding model builders are updated with extracted information.
5. **Dependency Resolution**: After traversal, dependencies between code blocks are established.

## 🔧 Key Functions

### Module-Level Processing

-   `visit_Module`: Extracts module-level information (docstring, header, footer, content)
-   `visit_Import` and `visit_ImportFrom`: Process import statements
-   `gather_standalone_lines`: Identifies standalone code blocks

### Class Processing

-   `visit_ClassDef`: Initiates class model building
-   `process_class_def`: Extracts class details (bases, decorators, etc.)

### Function Processing

-   `visit_FunctionDef`: Initiates function model building
-   `process_func_def`: Extracts function details (parameters, return annotations, etc.)
-   `process_parameters`: Processes function parameters

### Utility Functions

-   `extract_important_comment`: Identifies and extracts significant comments
-   `extract_type_annotation`: Processes type annotations in the code

## 🔄 Dependency Management

The `gather_and_set_children_dependencies` function is called at the end of module processing to establish relationships between different code blocks within the module.

## 🚧 Current Limitations and Future Enhancements

1. **Nested Class and Function Handling**: The current implementation may not fully capture the complexity of deeply nested class and function definitions.

2. **Advanced Python Features**: Some advanced Python features (e.g., decorators with complex arguments, type hints using `typing` module) may not be fully represented in the current model.

3. **Performance Optimization**: For very large codebases, the visitor's performance could potentially be improved through parallelization or incremental processing.

## 🤝 Contributing to Fenec Visitors

While the visitor system is internal, contributions to improve its functionality are welcome. Areas for potential enhancement include:

-   Testing, and error handling to ensure robustness and maintainability
-   Expanding the range of Python constructs that can be accurately modeled
-   Improving the efficiency of the tree traversal and model building process
-   Enhancing the dependency resolution mechanism

Please refer to the main Fenec [Contributing Guidelines](../../CONTRIBUTING.md) for more information on how to contribute to the project.

## 📚 Related Components

-   **Model Builders**: Work in tandem with visitors to construct detailed models of code structures.
-   **ID Generation Strategies**: Provide unique identifiers for various code blocks.
-   **Processing Context**: Manages contextual information during the visiting process.

For a comprehensive understanding of Fenec's architecture, please refer to the main [Fenec Documentation](../../README.md).
