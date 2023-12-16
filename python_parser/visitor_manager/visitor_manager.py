import json
import logging
from pathlib import Path
from python_parser.model_builders.module_model_builder import ModuleModelBuilder
from python_parser.utilities.logger.decorators import logging_decorator

from python_parser.parsers.python_parser import PythonParser
from python_parser.visitor_manager.import_and_dependency_update_functions import (
    ImportAndDependencyUpdater,
)
from python_parser.models.models import ModuleModel

from ai_services.summarizer_protocol import Summarizer
from python_parser.visitor_manager.summarization_manager import SummarizationManager

EXCLUDED_DIRECTORIES: set[str] = {".venv", "node_modules", "__pycache__", ".git"}


class VisitorManager:
    """
    Manages the visiting and processing of Python files in a given directory.

    This class scans a specified directory, filters for Python files, parses them, and saves the parsed data in a structured JSON format. It also maintains a mapping of directories to the Python files they contain.

    Attributes:
        directory (str): The root directory to scan for Python files.
        output_directory (str): The directory where output JSON files will be saved.
        directory_modules (dict): A mapping of directories to their contained Python files.

    Example:
        >>> visitor_manager = VisitorManager("/path/to/python/code", "output")
        >>> visitor_manager.process_files()
        # This will process all Python files in /path/to/python/code and save their parsed data in the output directory.

        # If you want to save a mapping of directories to Python files, you can call the save_visited_directories method.
        >>> visitor_manager.save_visited_directories()
    """

    @logging_decorator(message="Initializing VisitorManager")
    def __init__(
        self, summarizer: Summarizer, directory: str, output_directory: str = "output"
    ) -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self._create_output_directory()
        self.directory_modules: dict[str, list[str]] = {}

        self.summarizer: Summarizer = summarizer

    def process_files(self) -> None:
        """
        Processes each Python file found in the specified directory.

        For each Python file, this method updates the directory_modules with the file's information, parses the file, and saves the parsed data as JSON.

        Example:
            >>> visitor_manager.process_files()
            # Processes all Python files and saves their parsed data.
        """

        logging.info("Processing files")
        python_files: list[str] = self._get_python_files()
        model_save_context_list: list[tuple[ModuleModelBuilder, str]] = []
        for file_path in python_files:
            if model_builder := self._process_file(file_path):
                model_save_context_list.append((model_builder, file_path))

        logging.info("File processing completed")
        logging.info("Updating imports")

        # TODO: Test making this a tuple of tuples, see if that solves the double update import issue
        model_builder_list: list[ModuleModelBuilder] = [
            model_save_context[0] for model_save_context in model_save_context_list
        ]
        model_builder_tuple: tuple[ModuleModelBuilder, ...] = tuple(model_builder_list)

        import_and_dependency_updater = ImportAndDependencyUpdater(model_builder_tuple)
        import_and_dependency_updater.update_imports()
        logging.info("Updated imports")

        # Move from here down
        summarization_manager = SummarizationManager(
            model_builder_tuple, self.summarizer
        )
        summarization_manager.create_and_add_summaries_to_builders()
        logging.info("Summarization complete")
        logging.info("Saving models as JSON")
        for model_save_context in model_save_context_list:
            module_model: ModuleModel = self._build_module_model(model_save_context[0])
            self._save_model_as_json(module_model, model_save_context[1])
        logging.info("JSON save complete")

    @logging_decorator(message="Saving visited directories")
    def save_visited_directories(
        self, directory_mape_name: str = "directory_map.json"
    ) -> None:
        """
        Saves a JSON file mapping each visited directory to its Python files.

        The output is saved in a file named '00_directory_module_map.json' within the specified output directory.

        Args:
            directory_mape_name (str): The name of the output file for the directory map.

        Example:
            >>> visitor_manager.save_visited_directories("directory_map.json")
            # Saves a mapping of directories to Python files as JSON.
        """

        output_path: str = self._get_directory_map_output_path(directory_mape_name)
        self._write_json_directory_map(output_path)

    def _create_output_directory(self) -> None:
        """Creates the output directory if it does not already exist."""

        Path(self.output_directory).mkdir(exist_ok=True)

    def _walk_directories(self) -> list[str]:
        """Walks the specified directory and returns a list of all files."""

        all_files: list[str] = []
        for file_path in Path(self.directory).rglob("*"):
            if not any(
                excluded in file_path.parts for excluded in EXCLUDED_DIRECTORIES
            ):
                all_files.append(str(file_path))
        return all_files

    def _filter_python_files(self, files: list[str]) -> list[str]:
        """Filters a list of files to only include Python files."""

        return [file for file in files if file.endswith(".py")]

    @logging_decorator(message="Getting Python files")
    def _get_python_files(self) -> list[str]:
        """Gets all Python files in the specified directory."""

        all_files: list[str] = self._walk_directories()
        return self._filter_python_files(all_files)

    def _process_file(self, file_path: str) -> ModuleModelBuilder | None:
        """Processes a single Python file."""

        file_path_obj = Path(file_path)
        root = str(file_path_obj.parent)
        self.directory_modules.setdefault(root, []).append(file_path_obj.name)
        return self._parse_file(file_path)

    @logging_decorator(message="Processing file")
    def _parse_file(self, file_path: str) -> ModuleModelBuilder | None:
        """Parses a Python file and saves the parsed data as JSON."""

        parser = PythonParser(file_path)
        code: str = parser.open_file()
        module_model_builder: ModuleModelBuilder | None = parser.parse(code)

        return module_model_builder

    @logging_decorator(message="Saving model as JSON")
    def _save_model_as_json(self, module_model: ModuleModel, file_path: str) -> None:
        """Saves a parsed ModuleModel as JSON."""

        json_output_directory: str = self._create_json_output_directory()
        output_path: str = self._get_json_output_path(file_path, json_output_directory)
        self._write_json_file(module_model, output_path)

    def _create_json_output_directory(self) -> str:
        """Creates the JSON output directory if it does not already exist."""

        json_output_directory: Path = Path(self.output_directory) / "json"
        json_output_directory.mkdir(exist_ok=True)
        return str(json_output_directory)

    def _get_json_output_path(self, file_path: str, json_output_directory: str) -> str:
        """Gets the output path for a JSON file."""

        relative_path: Path = Path(file_path).relative_to(Path(self.directory))
        safe_relative_path: str = str(relative_path).replace("/", ":").rstrip(".py")
        return str(Path(json_output_directory) / f"{safe_relative_path}.json")

    def _write_json_file(self, module_model: ModuleModel, output_path: str) -> None:
        """Writes a JSON file containing the parsed data from a ModuleModel."""

        parsed_data_json: str = module_model.model_dump_json(indent=4)
        with open(output_path, "w") as json_file:
            json_file.write(parsed_data_json)

    def _get_directory_map_output_path(self, directory_output_name: str) -> str:
        """Gets the output path for the directory map JSON file."""

        return str(Path(self.output_directory) / directory_output_name)

    def _write_json_directory_map(self, output_path: str) -> None:
        """Writes the directory map JSON file."""

        with open(output_path, "w") as json_file:
            json.dump(self.directory_modules, json_file, indent=4)

    def _build_module_model(
        self, visitor_stack: ModuleModelBuilder | None
    ) -> ModuleModel:
        """
        Builds a module model from the provided module builder.

        Args:
            visitor_stack (ModuleModelBuilder): The module builder to build the model from.

        Returns:
            ModuleModel: A structured module model.

        Example:
            >>> module_model = python_parser.build_module_model(visitor_stack)
            # Builds a module model from the provided module builder.
        """

        if not isinstance(visitor_stack, ModuleModelBuilder):
            raise TypeError("Expected the first builder to be a ModuleModelBuilder")

        return visitor_stack.build()
