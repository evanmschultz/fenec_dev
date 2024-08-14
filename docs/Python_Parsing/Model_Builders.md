# 🏗️ Fenec Model Builders

The Model Builders in Fenec are responsible for constructing detailed representations of different code elements within a Python project. These builders follow the Builder pattern, providing a flexible and extensible way to create complex model objects for modules, classes, functions, and standalone code blocks.

## 🌟 Features

-   🧱 Hierarchical builder structure reflecting code relationships
-   🔧 Specialized builders for different code elements (modules, classes, functions, standalone blocks)
-   🔄 Consistent interface across different builder types
-   🧩 Extensible design for potential future code element types
-   🏭 Factory pattern for creating appropriate builders

> **NOTE:** The Model Builders in Fenec are internal structures used for code analysis and are not intended for direct interaction by end-users. They are designed to be used by Fenec's code analysis pipeline to parse, store, and analyze code structures. The documentation is provided for reference and internal development purposes and should be used for diagnosing issues, extending Fenec's functionality, or gaining a better understanding of how Fenec works.

## 🧩 Core Components

### BaseModelBuilder (Abstract Base Class)

This abstract base class defines the common interface and functionality for all specific model builders:

-   Common attributes management (id, file path, line numbers, etc.)
-   Child builder and model management
-   Dependency and import handling
-   Abstract `build()` method to be implemented by concrete builders

### Concrete Builders

1. **ModuleModelBuilder**

    - Builds models for Python module files
    - Handles module-specific attributes like docstrings, headers, footers, and imports

2. **ClassModelBuilder**

    - Builds models for Python classes
    - Manages class-specific attributes such as decorators, base classes, and keywords

3. **FunctionModelBuilder**

    - Builds models for Python functions and methods
    - Handles function-specific attributes like parameters, return types, and async status

4. **StandaloneBlockModelBuilder**
    - Builds models for standalone code blocks within modules
    - Manages attributes specific to standalone blocks, such as variable assignments

### BuilderFactory

A factory class that creates instances of the appropriate model builder based on the block type:

-   Uses a strategy pattern to map block types to builder creation functions
-   Provides type-safe creation methods for different builder types

## 🚀 Usage

Here's a basic example of how to use the Model Builders:

```python
from fenec.python_parser.model_builders.builder_factory import BuilderFactory
from fenec.models.enums import BlockType

# Create a module builder
module_builder = BuilderFactory.create_builder_instance(
    block_type=BlockType.MODULE,
    id="module_1",
    file_path="/path/to/module.py",
    parent_id=None
)

# Configure the module builder
module_builder.set_start_line_num(1) \
              .set_end_line_num(100) \
              .set_code_content("...") \
              .set_docstring("This is a module docstring")

# Create a class builder as a child of the module
class_builder = BuilderFactory.create_builder_instance(
    block_type=BlockType.CLASS,
    id="class_1",
    name="MyClass",
    parent_id="module_1",
    file_path="/path/to/module.py"
)

# Add the class builder as a child of the module builder
module_builder.add_child_builder(class_builder)

# Build the module model (which will also build all child models)
module_model, child_models = module_builder.build()
```

## 🔄 Integration with Models

The Model Builders work hand-in-hand with the Fenec model classes:

-   Each builder corresponds to a specific model type (e.g., `ModuleModelBuilder` builds `ModuleModel` instances)
-   Builders handle the complexities of constructing hierarchical model structures
-   The `build()` method of each builder returns the fully constructed model instance

## 🚧 Under Development

The Model Builder system in Fenec is under active development. Current areas of focus include:

-   Optimizing the building process for large-scale projects
-   Enhancing support for more complex Python language features
-   Improving error handling and validation during the build process

## 🤝 Contributing

We welcome contributions to improve and expand the Model Builders in Fenec! If you have ideas for better building strategies or enhanced model representations, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests!
-   Any additional suggestions are welcome; just make an issue or pull request.

## 🗺️ Roadmap

The future development of Fenec's Model Builders will focus on:

1. Addition of builders for directory models and project models (if and/or when the the project model is implemented).

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's Model Builders and look forward to your contributions in making them even more powerful and versatile!
