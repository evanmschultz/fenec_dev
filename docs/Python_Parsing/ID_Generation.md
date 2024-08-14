# 🆔 Fenec ID Generation Strategies

The ID Generation Strategies in Fenec are responsible for creating unique identifiers for different code elements within a project. These strategies play a crucial role in maintaining a consistent and meaningful identification system across the entire codebase and are designed to maintain the project's structure in their naming itself.

## 🌟 Features

-   🏗️ Abstract base class for defining a common interface
-   🔢 Unique ID generation for modules, classes, functions, standalone code blocks, and directories
-   🔗 Hierarchical ID structure reflecting code relationships
-   🔄 Consistent ID format across different code elements
-   🧩 Extensible design for potential future ID generation needs

## 🧩 Core Components

### IDGenerationStrategy (Abstract Base Class)

This abstract base class defines the interface for all ID generation strategies:

-   `generate_id(**kwargs) -> str`: Abstract method to be implemented by concrete strategies.

### Concrete Strategies

1. **ModuleIDGenerationStrategy**

    - Generates IDs for Python module files.
    - Method: `generate_id(file_path: str) -> str`
    - Format: `{converted_file_path}__*__MODULE`

2. **ClassIDGenerationStrategy**

    - Generates IDs for Python classes.
    - Method: `generate_id(parent_id: str, class_name: str) -> str`
    - Format: `{parent_id}__*__CLASS-{class_name}`

3. **FunctionIDGenerationStrategy**

    - Generates IDs for Python functions or methods.
    - Method: `generate_id(parent_id: str, function_name: str) -> str`
    - Format: `{parent_id}__*__FUNCTION-{function_name}`

4. **StandaloneCodeBlockIDGenerationStrategy**

    - Generates IDs for standalone code snippets within a module.
    - Method: `generate_id(parent_id: str, count: int) -> str`
    - Format: `{parent_id}__*__STANDALONE_BLOCK-{count}`

5. **DirectoryIDGenerationStrategy**
    - Generates IDs for directories in the project structure.
    - Method: `generate_id(directory_path: str) -> str`
    - Format: `{converted_directory_path}__*__DIRECTORY`

## 🚀 Usage

These ID generation strategies are typically used in conjunction with their corresponding model classes. Here's a basic example of how they might be used:

```python
from fenec.id_generators import ModuleIDGenerationStrategy, ClassIDGenerationStrategy

# Generate a module ID
module_id = ModuleIDGenerationStrategy.generate_id("/path/to/module.py")
print(module_id)  # Output: path:to:module.py__*__MODULE

# Generate a class ID
class_id = ClassIDGenerationStrategy.generate_id(module_id, "MyClass")
print(class_id)  # Output: path:to:module.py__*__MODULE__*__CLASS-MyClass
```

## 🔄 Integration with Models

The ID generation strategies are designed to work seamlessly with the Fenec model classes:

-   Each model (e.g., `ModuleModel`, `ClassModel`) uses its corresponding ID generation strategy to create unique identifiers.
-   The hierarchical nature of the IDs reflects the structure of the code, making it easy to understand relationships between different code elements.

## 🚧 Under Development

The ID generation system in Fenec is under active development. Current areas of focus include:

-   Optimizing ID generation for large-scale projects
-   Ensuring ID uniqueness across complex codebases
-   Exploring more compact ID formats while maintaining readability

## 🤝 Contributing

We welcome contributions to improve and expand the ID generation strategies in Fenec! If you have ideas for better ID formats or enhanced generation strategies, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Testing!
-   Any suggestions or changes are welcome, just make an issue or pull request.

We appreciate your interest in Fenec's ID generation strategies and look forward to your contributions in making them even more robust and versatile!
