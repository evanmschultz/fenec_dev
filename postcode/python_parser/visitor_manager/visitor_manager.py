from dataclasses import dataclass
import logging
from pathlib import Path

from postcode.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)
from postcode.utilities.logger.decorators import logging_decorator

from postcode.python_parser.parsers.python_parser import PythonParser
from postcode.python_parser.visitor_manager.import_and_dependency_updater import (
    ImportAndDependencyUpdater,
)
from postcode.python_parser.models.models import ModuleModel

from postcode.ai_services.summarizer.summarization_context import Summarizer

EXCLUDED_DIRECTORIES: set[str] = {".venv", "node_modules", "__pycache__", ".git"}


@dataclass
class VisitorManagerProcessFilesReturn:
    """
    Represents the return value of the VisitorManager.process_files() method.

    Attributes:
        models_tuple (tuple[ModuleModel, ...]): A tuple of ModuleModel objects representing the parsed modules.
        directory_modules (dict[str, list[str]]): A dictionary mapping directory paths to lists of module names.
            This is used to keep track of the modules present in each directory.
    """

    models_tuple: tuple[ModuleModel, ...]
    directory_modules: dict[str, list[str]]


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
    """

    @logging_decorator(message="Initializing VisitorManager")
    def __init__(
        self, summarizer: Summarizer, directory: str, output_directory: str = "output"
    ) -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self.directory_modules: dict[str, list[str]] = {}

        self.summarizer: Summarizer = summarizer

    def process_files(self) -> VisitorManagerProcessFilesReturn:
        """
        Process the files in the directory and return the module models.

        This function iterates through all the Python files in the directory, processes each file,
        updates the imports, and builds module models for each file. It returns a tuple of module models
        and a dictionary of directory modules.

        Returns:
            A named tuple (VisitorManagerProcessFilesReturn) containing:
            - models_tuple (tuple[ModuleModel, ...]): A tuple of module models.
            - directory_modules (dict[str, ModuleModel]): A dictionary of directory modules.

        Examples:
            >>> visitor_manager = VisitorManager()
            >>> result = visitor_manager.process_files()
            >>> print(result.models_tuple)
            (ModuleModel(file_path='/path/to/file1.py'), ModuleModel(file_path='/path/to/file2.py'))
            >>> print(result.directory_modules)
            {'/path/to/directory1': ModuleModel(file_path='/path/to/directory1/__init__.py')}
        """

        logging.info("Processing files")
        python_files: list[str] = self._get_python_files()
        model_builder_list: list[ModuleModelBuilder] = []
        for file_path in python_files:
            if model_builder := self._process_file(file_path):
                model_builder_list.append((model_builder))

        logging.info("File processing completed")
        logging.info("Updating imports")

        # TODO: Test making this a tuple of tuples, see if that solves the double update import issue
        model_builder_tuple: tuple[ModuleModelBuilder, ...] = tuple(model_builder_list)

        import_and_dependency_updater = ImportAndDependencyUpdater(model_builder_tuple)
        import_and_dependency_updater.update_imports()
        logging.info("Updated imports")

        module_models_list: list[ModuleModel] = []
        for module_model_builder in model_builder_tuple:
            module_model: ModuleModel = self._build_module_model(module_model_builder)
            module_models_list.append(module_model)

        module_models_tuple: tuple[ModuleModel, ...] = tuple(module_models_list)

        return VisitorManagerProcessFilesReturn(
            models_tuple=module_models_tuple, directory_modules=self.directory_modules
        )

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
