from typing import TYPE_CHECKING, Union
import libcst
from libcst.metadata import MetadataWrapper
from postcode.python_parser.id_generation.id_generation_strategies import (
    ModuleIDGenerationStrategy,
)
from postcode.python_parser.model_builders.builder_factory import BuilderFactory
from postcode.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)

from postcode.python_parser.visitors.module_visitor import ModuleVisitor
from postcode.models.enums import BlockType

if TYPE_CHECKING:
    from postcode.python_parser.model_builders.class_model_builder import (
        ClassModelBuilder,
    )
    from postcode.python_parser.model_builders.function_model_builder import (
        FunctionModelBuilder,
    )
    from postcode.python_parser.model_builders.standalone_block_model_builder import (
        StandaloneBlockModelBuilder,
    )


BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]


class PythonParser:
    """
    A parser for Python source code, using libcst to parse and construct a module model.

    This class takes the path to a Python file, reads its contents, and parses it into a structured
    module model using the libcst library. It is designed to work with a specific file at a time.

    Attributes:
        file_path (str): The path to the Python file to be parsed.

    Example:
        >>> python_parser = PythonParser("/path/to/python/file.py")
        >>> module_model = python_parser.parse(python_parser.open_file())
        # This will parse the specified Python file and return a structured module model.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def open_file(self) -> str:
        """
        Opens and reads the contents of the Python file specified in the file_path attribute.

        Returns:
            str: The contents of the file as a string.

        Example:
            >>> code = python_parser.open_file()
            # Reads and returns the contents of the Python file.
        """

        with open(self.file_path, "r") as file:
            return file.read()

    def parse(self, code: str) -> ModuleModelBuilder | None:
        """
        Parses the provided Python code into a structured module model.

        Uses libcst to parse the provided code using the ModuleVisitor class. A ModuleModelBuilder instance is returned
        along with it hierarchy of child builders.

        Args:
            - code (str): The Python code to be parsed.

        Returns:
            - ModuleModelBuilder | None: The module model builder for the provided code.

        Example:
            ```Python
            code = python_parser.open_file()
            module_model = python_parser.parse(code)
            # Parses the provided code and returns a module model builder.
            ```
        """

        wrapper = MetadataWrapper(libcst.parse_module(code))
        module_id: str = ModuleIDGenerationStrategy.generate_id(
            file_path=self.file_path
        )
        module_builder: ModuleModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.MODULE, id=module_id, file_path=self.file_path
        )
        visitor = ModuleVisitor(id=module_id, module_builder=module_builder)
        wrapper.visit(visitor)

        return (
            visitor.builder_stack[0]
            if isinstance(visitor.builder_stack[0], ModuleModelBuilder)
            else None
        )
