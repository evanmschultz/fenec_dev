# 🐍 Fenec Python Parser

The Python Parser in Fenec is responsible for analyzing Python source code and constructing structured representations of the code using the Model Builders. It leverages the `libcst` library to parse Python code and create a comprehensive model of the code structure.

## 🌟 Features

-   📂 File-based parsing of Python source code
-   🔍 Detailed analysis of Python modules, classes, functions, and standalone code blocks
-   🏗️ Integration with Model Builders for constructing hierarchical code representations
-   🔗 Support for maintaining parent-child relationships between code elements
-   🔄 Flexible parsing process adaptable to different code structures

> **NOTE:** The Python Parser is an internal component of Fenec used for code analysis and model construction. It is not meant for direct interaction by end-users. The documentation is provided for reference and internal development purposes and should be used for diagnosing issues, extending Fenec's functionality, or gaining a better understanding of how Fenec works.

## 🧩 Core Components

### PythonParser

The main class responsible for parsing Python source code:

-   `__init__(self, file_path: str)`: Initializes the parser with a file path.
-   `open_file(self) -> str`: Reads and returns the contents of the specified Python file.
-   `parse(self, code: str, parent_id: str) -> ModuleModelBuilder | None`: Parses the provided code and returns a ModuleModelBuilder instance.

### Key Dependencies

-   **libcst**: Used for parsing Python code into a Concrete Syntax Tree (CST).
-   **ModuleVisitor**: A custom visitor class that traverses the CST and constructs the module model.
-   **BuilderFactory**: Used to create appropriate model builders for different code elements.
-   **ID Generation Strategies**: Used to generate unique identifiers for code elements.

## 🚀 Usage

Here's a basic example of how to use the Python Parser:

```python
from fenec.python_parser.python_parser import PythonParser

# Initialize the parser with a file path
parser = PythonParser("/path/to/your/python_file.py")

# Read the file contents
code = parser.open_file()

# Parse the code
module_builder = parser.parse(code, parent_id="parent_module_id")

if module_builder:
    # Build the module model
    module_model, child_models = module_builder.build()

    # Now you have a structured representation of your Python file
    print(f"Module Name: {module_model.file_path}")
    print(f"Number of children: {len(module_model.children_ids)}")
else:
    print("Failed to parse the module")
```

## 🔄 Integration with Other Components

The Python Parser works closely with other Fenec components:

-   **Model Builders**: The parser uses various model builders to construct representations of different code elements.
-   **Visitors**: Custom visitor classes (like ModuleVisitor) are used to traverse the CST and populate the model builders.
-   **ID Generation Strategies**: These are used to create unique identifiers for each code element.

## 🚧 Under Development

The Python Parser in Fenec is under active development. Current areas of focus include:

-   Testing, and error handling to ensure robustness and reliability
-   Improving parsing performance for large Python files, if necessary, this can include parallelization or concurrent processing
-   Enhancing support for more complex Python language features
-   Refining the integration between the parser and model builders

## 🤝 Contributing

We welcome contributions to improve and expand the Python Parser in Fenec! If you have ideas for enhancing the parsing process or supporting additional Python features, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Testing and error handling to ensure robustness and reliability
-   Performance optimizations for large-scale codebases
-   Any additional suggestions or changes are welcome, just make an issue or pull request.

We appreciate your interest in Fenec's Python Parser and look forward to your contributions in making it even more powerful and versatile!
