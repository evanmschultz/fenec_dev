from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Union

from postcode.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)
from postcode.utilities.logger.decorators import logging_decorator

from postcode.python_parser.parsers.python_parser import PythonParser
from postcode.python_parser.visitor_manager.import_and_dependency_updater import (
    ImportAndDependencyUpdater,
)
from postcode.models.models import (
    ClassModel,
    DirectoryModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)


from postcode.python_parser.model_builders.class_model_builder import (
    ClassModelBuilder,
)
from postcode.python_parser.model_builders.function_model_builder import (
    FunctionModelBuilder,
)
from postcode.python_parser.model_builders.standalone_block_model_builder import (
    StandaloneBlockModelBuilder,
)

from postcode.python_parser.id_generation.id_generation_strategies import (
    ModuleIDGenerationStrategy,
    DirectoryIDGenerationStrategy,
)
from postcode.types.postcode import ModelType


BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]

# ModelType = Union[
#     ModuleModel,
#     ClassModel,
#     FunctionModel,
#     StandaloneCodeBlockModel,
#     DirectoryModel,
# ]

EXCLUDED_DIRECTORIES: set[str] = {".venv", "node_modules", "__pycache__", ".git"}


@dataclass
class VisitorManagerProcessFilesReturn:
    """
    Represents the return value of the VisitorManager.process_files() method.

    Attributes:
        - models_tuple (tuple[ModuleModel, ...]): A tuple of ModuleModel objects representing the parsed modules.
        - directory_modules (dict[str, list[str]]): A dictionary mapping directory paths to lists of module names.
            This is used to keep track of the modules present in each directory.
    """

    models_tuple: tuple[ModelType, ...]
    directory_modules: dict[str, list[str]]


@dataclass
class DirectoryDetails:
    """
    Represents the details of a directory.

    Attributes:
        - directory_name (str): The name of the directory.
        - sub_directories (list[str]): A list of the names of the sub-directories of the directory.
        - module_ids (list[str]): A list of the module ids of the modules in the directory.
    """

    directory_name: str
    sub_directories: list[str]
    module_ids: list[str]


class VisitorManager:
    """
    Manages the visiting and processing of Python files in a given directory.

    This class scans a specified directory, filters for Python files, parses them, and saves the parsed data in a structured JSON format.
    It also maintains a mapping of directories to the Python files they contain.

    Attributes:
        - directory (str): The root directory to scan for Python files.
        - directory_modules (dict[str, list[str]]): A mapping of directories to their contained Python files.

    Example:
        ```Python
        visitor_manager = VisitorManager("/path/to/python/code")
        visitor_manager.process_files()
        # This will process all Python files in /path/to/python/code and save their parsed data in the output directory.
        ```
    """

    @logging_decorator(message="Initializing VisitorManager")
    def __init__(self, directory: str) -> None:
        self.directory: str = directory
        self.directory_modules: dict[str, list[str]] = {}

    def process_files(self) -> VisitorManagerProcessFilesReturn:
        """
        Process the files in the directory and return the module models.

        This function iterates through all the Python files in the directory, processes each file,
        updates the imports, and builds module models for each file. It returns a tuple of module models
        and a dictionary of directory modules.

        Returns:
            - VisitorManagerProcessFilesReturn, a named tuple containing:
                - models_tuple (tuple[ModuleModel, ...]): A tuple of module models.
                - directory_modules (dict[str, ModuleModel]): A dictionary of directory modules.

        Examples:
            ```Python
            visitor_manager = VisitorManager()
            result = visitor_manager.process_files()
            print(result.models_tuple)
            # (ModuleModel(file_path='/path/to/file1.py'), ModuleModel(file_path='/path/to/file2.py'))
            print(result.directory_modules)
            {'/path/to/directory1': ModuleModel(file_path='/path/to/directory1/__init__.py')}
            ```
        """

        logging.info("Processing files")
        python_files: list[str] = self._get_python_files()
        model_builder_list: list[ModuleModelBuilder] = []
        for file_path in python_files:
            if model_builder := self._process_file(file_path):
                model_builder_list.append((model_builder))

        logging.info("File processing completed")
        logging.info("Updating imports")

        model_builder_tuple: tuple[ModuleModelBuilder, ...] = tuple(model_builder_list)

        import_and_dependency_updater = ImportAndDependencyUpdater(model_builder_tuple)
        import_and_dependency_updater.update_imports()
        logging.info("Updated imports")

        models_list: list[
            ModuleModel | ClassModel | FunctionModel | StandaloneCodeBlockModel
        ] = []
        for module_model_builder in model_builder_tuple:
            module_model_return: tuple[
                ModuleModel,
                list[ClassModel | FunctionModel | StandaloneCodeBlockModel] | None,
            ] = self._build_module_model(module_model_builder)
            models_list.append(module_model_return[0])
            if module_model_return[1]:
                models_list.extend(module_model_return[1])

        directory_models_list: list[DirectoryModel] = []
        for directory_path in self.directory_modules.keys():
            directory_model: DirectoryModel = self._build_directory_model(
                directory_path
            )
            directory_models_list.append(directory_model)

        all_models: list[ModelType] = [
            *models_list,
            *directory_models_list,
        ]

        models_tuple: tuple[ModelType, ...] = tuple(all_models)

        return VisitorManagerProcessFilesReturn(
            models_tuple=models_tuple, directory_modules=self.directory_modules
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

        parent_id: str | None = self._get_parent_directory_id(file_path)
        if not parent_id:
            parent_id = ""

        module_model_builder: ModuleModelBuilder | None = parser.parse(code, parent_id)

        return module_model_builder if module_model_builder else None

    def _build_module_model(
        self, visitor_stack: ModuleModelBuilder | None
    ) -> tuple[
        ModuleModel, list[ClassModel | FunctionModel | StandaloneCodeBlockModel] | None
    ]:
        """
        Builds a module model from the provided module builder.

        Args:
            - visitor_stack (ModuleModelBuilder): The module builder to build the model from.

        Returns:
            - ModuleModel: A structured module model.
        """

        if not isinstance(visitor_stack, ModuleModelBuilder):
            raise TypeError("Expected the first builder to be a ModuleModelBuilder")

        return visitor_stack.build()

    def _build_directory_model(self, directory_path: str) -> DirectoryModel:
        """Builds a directory model for the given directory path."""

        id: str = DirectoryIDGenerationStrategy().generate_id(directory_path)
        parent_id: str | None = self._get_parent_directory_id(directory_path)

        return DirectoryModel(
            id=id,
            parent_id=parent_id,
            directory_name=self._get_directory_name(directory_path),
            sub_directories_ids=self._get_subdirectory_ids(directory_path),
            children_ids=self._generate_module_ids(directory_path),
        )

    def _get_subdirectory_ids(self, directory_path: str) -> list[str]:
        """Gets the sub-directories of the given directory."""

        subdirectories: list[str] = [
            directory.name
            for directory in Path(directory_path).iterdir()
            if directory.is_dir() and directory.name not in EXCLUDED_DIRECTORIES
        ]

        subdirectory_ids: list[str] = [
            DirectoryIDGenerationStrategy().generate_id(
                str(Path(directory_path) / subdirectory)
            )
            for subdirectory in subdirectories
        ]

        return subdirectory_ids

    def _get_directory_name(self, directory_path: str) -> str:
        """Gets the name of the given directory."""

        return Path(directory_path).name

    def _generate_module_ids(self, directory_path: str) -> list[str]:
        """Generates module ids for the given directory."""

        file_names: list[str] = self.directory_modules.get(directory_path, [])
        python_files: list[str] = self._filter_python_files(file_names)

        return [
            ModuleIDGenerationStrategy.generate_id(str(Path(directory_path) / module))
            for module in python_files
        ]

    def _get_parent_directory_id(self, directory_path: str) -> str | None:
        """Gets the parent id of the given directory."""

        parent_path: str = str(Path(directory_path).parent)
        if parent_path == self.directory:
            return None
        else:
            return DirectoryIDGenerationStrategy().generate_id(parent_path)
