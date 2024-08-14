# 📁 JSON Handler

The JSON Handler in Fenec is a utility class designed to facilitate the serialization and storage of parsed code models in JSON format. Its primary purpose is to allow for easier visualization of outputs during development, providing a human-readable representation of the parsed code structures.

> **⚠️ Note:** The JSON Handler is primarily a development tool and may be eliminated in future versions of Fenec unless specific use cases for end-users are identified. Its current implementation is not intended for production use but rather for debugging and development purposes.

## 🌟 Features

-   💾 Serialization of parsed code models to JSON format
-   📂 Organized storage of JSON outputs in a dedicated directory structure
-   🗺️ Generation of a directory map for visited Python files
-   🧹 Automatic cleanup of previous output directories

## 🧩 Components

### JSONHandler

The `JSONHandler` class is responsible for managing the serialization and storage of parsed code models.

#### Key Methods:

-   `save_model_as_json`: Saves a parsed ModelType as JSON.
-   `save_visited_directories`: Saves a JSON file mapping each visited directory to its Python files.

#### Private Methods:

-   `_create_output_directory`: Creates the main output directory.
-   `_create_json_output_directory`: Creates a subdirectory for JSON outputs.
-   `_get_json_output_path`: Determines the output path for a JSON file.
-   `_write_json_file`: Writes a JSON file containing the parsed data from a ModelType.
-   `_get_directory_map_output_path`: Gets the output path for the directory map JSON file.
-   `_write_json_directory_map`: Writes the directory map JSON file.
-   `_clean_output_directory`: Deletes the output directory and all its contents.

## 🚀 Usage

Here's a basic example of how to use the JSON Handler:

```python
from fenec.utilities.json_handler import JSONHandler
from fenec.models.models import ModuleModel

# Initialize the JSON Handler
handler = JSONHandler(directory="/path/to/code", directory_modules={})

# Create a sample module model
module_model = ModuleModel(id='module1', file_path='/path/to/code/module1.py')

# Save the model as JSON
handler.save_model_as_json(module_model, file_path='/path/to/code/module1.py')

# Save the directory map
handler.save_visited_directories()
```

## 🚧 Development Tool

The JSON Handler is primarily intended for development and debugging purposes. It provides the following benefits during the development process:

1. **Visualization**: Allows developers to easily inspect the structure of parsed code models.
2. **Debugging**: Facilitates the identification of parsing issues or unexpected model structures.
3. **Documentation**: Provides a human-readable representation of the code structure, which can be useful for documentation or manual verification.

## 🔮 Future Considerations

As Fenec evolves, the role of the JSON Handler may change:

1. **Potential Elimination**: Unless specific use cases for end-users are identified, the JSON Handler may be removed from future versions of Fenec to streamline the codebase.
2. **Alternative Visualizations**: More sophisticated visualization tools may replace the JSON output for debugging and development purposes.
3. **User-Facing Features**: If valuable use cases are identified, the JSON Handler could be evolved into a user-facing feature for exporting code structures.

## 🤝 Contributing

While the JSON Handler is primarily a development tool, contributions that enhance its utility for debugging or extend its functionality in valuable ways are welcome. If you have ideas for improving the JSON Handler or integrating it more deeply into the development process, please check our [Contributing Guidelines](../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

## 🗺️ Roadmap

The future of the JSON Handler will be determined by its utility in the development process and any potential use cases identified for end-users. For now, it remains a valuable tool for developers working on Fenec.

For a more comprehensive view of Fenec's plans, including the potential evolution or deprecation of development tools like the JSON Handler, please refer to our [Roadmap](../ROADMAP.md).

We appreciate your interest in Fenec's development tools and welcome any insights on how we can improve our development and debugging processes!
