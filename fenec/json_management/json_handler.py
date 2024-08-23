import json
import logging
from pathlib import Path
from shutil import rmtree
from typing import Union

from fenec.models.models import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
)
from fenec.utilities.logger.decorators import logging_decorator

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
]


class JSONHandler:
    """
    A class for handling the serialization and storage of parsed code models in JSON format.

    This class provides methods to save parsed code models, such as modules, classes, functions, standalone code blocks, and directory maps, as JSON files. It ensures proper organization and cleanup of the output directory.

    Attributes:
        - directory (str): The base directory of the parsed code.
        - output_directory (str): The directory where JSON output files are stored.
        - directory_modules (dict[str, list[str]]): A mapping of directories to their corresponding Python files.

    Example:
        ```Python
        # This example demonstrates how to use JSONHandler to save a parsed model as JSON.
        handler = JSONHandler(directory="/path/to/code", directory_modules={})
        module_model = ModuleModel(id='module1', file_path='/path/to/code/module1.py')
        handler.save_model_as_json(module_model, file_path='/path/to/code/module1.py')
        ```
    """

    def __init__(
        self,
        directory: str,
        directory_modules: dict[str, list[str]],
        output_directory: str = "output_json",
    ) -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self.directory_modules: dict[str, list[str]] = directory_modules

        self._clean_output_directory()
        self._create_output_directory()

    @logging_decorator(message="Saving model as JSON")
    def save_model_as_json(
        self,
        model: ModelType,
        file_path: str,
    ) -> None:
        """
        Saves a parsed ModelType as JSON.

        Args:
            - model (ModelType): The parsed code model to be saved.
            - file_path (str): The file path of the original Python file.

        Example:
            ```Python
            # This example demonstrates how to use JSONHandler to save a parsed model as JSON.
            handler = JSONHandler(directory="/path/to/code", directory_modules={})
            module_model = ModuleModel(id='module1', file_path='/path/to/code/module1.py')
            handler.save_model_as_json(module_model, file_path='/path/to/code/module1.py')
            ```
        """

        json_output_directory: str = self._create_json_output_directory()
        output_path: str = self._get_json_output_path(file_path, json_output_directory)
        self._write_json_file(model, output_path)

    @logging_decorator(message="Saving visited directories")
    def save_visited_directories(
        self, directory_map_name: str = "directory_map.json"
    ) -> None:
        """
        Saves a JSON file mapping each visited directory to its Python files.

        The output is saved in a file named 'directory_map.json' within the specified output directory.

        Args:
            - directory_map_name (str, optional): The name of the output file for the directory map. Defaults to "directory_map.json".

        Example:
            ```Python
            # This example demonstrates how to save visited directories as a JSON map.
            handler = JSONHandler(directory="/path/to/code", directory_modules={})
            handler.save_visited_directories(directory_map_name="custom_map.json")
            ```
        """

        output_path: str = self._get_directory_map_output_path(directory_map_name)
        self._write_json_directory_map(output_path)

    def _create_output_directory(self) -> None:
        """Creates the output directory if it does not already exist."""

        Path(self.output_directory).mkdir(exist_ok=True)

    def _create_json_output_directory(self) -> str:
        """
        Creates the JSON output directory if it does not already exist.

        Returns:
            str: The path to the created JSON output directory.
        """

        json_output_directory: Path = Path(self.output_directory) / "json"
        json_output_directory.mkdir(exist_ok=True)
        return str(json_output_directory)

    def _get_json_output_path(self, file_path: str, json_output_directory: str) -> str:
        """
        Gets the output path for a JSON file.

        Args:
            - file_path (str): The file path of the original Python file.
            - json_output_directory (str): The path to the JSON output directory.

        Returns:
            str: The output path for the JSON file.
        """

        # TODO: Find better solution, only if json output will remain in the future for debugging
        if len(file_path) > 50:
            file_path = file_path[:50]

        if "DIRECTORY" in file_path:
            safe_file_path: str = file_path.replace("/", ":")
            return str(Path(json_output_directory) / f"{safe_file_path}.json")
        else:
            relative_path: Path = Path(file_path).relative_to(Path(self.directory))
            safe_relative_path: str = str(relative_path).replace("/", ":").rstrip(".py")
            return str(Path(json_output_directory) / f"{safe_relative_path}.json")

    def _write_json_file(
        self,
        module_model: ModelType,
        output_path: str,
    ) -> None:
        """
        Writes a JSON file containing the parsed data from a ModuleModel.

        Args:
            - module_model (ModelType): The parsed code model.
            - output_path (str): The path where the JSON file will be saved.
        """

        parsed_data_json: str = module_model.model_dump_json(indent=4)
        with open(output_path, "w") as json_file:
            json_file.write(parsed_data_json)

    def _get_directory_map_output_path(self, directory_output_name: str) -> str:
        """
        Gets the output path for the directory map JSON file.

        Args:
            - directory_output_name (str): The name of the output file for the directory map.

        Returns:
            str: The output path for the directory map JSON file.
        """

        return str(Path(self.output_directory) / directory_output_name)

    def _write_json_directory_map(self, output_path: str) -> None:
        """Writes the directory map JSON file."""

        with open(output_path, "w") as json_file:
            json.dump(self.directory_modules, json_file, indent=4)

    def _clean_output_directory(self) -> None:
        """Deletes the output directory and all its contents."""

        output_dir = Path(self.output_directory)
        if output_dir.exists() and output_dir.is_dir():
            rmtree(output_dir)
