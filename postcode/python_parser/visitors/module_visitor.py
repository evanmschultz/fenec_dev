import libcst

from postcode.python_parser.id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
)

from postcode.python_parser.model_builders.builder_factory import BuilderFactory
from postcode.python_parser.model_builders.class_model_builder import ClassModelBuilder
from postcode.python_parser.model_builders.function_model_builder import (
    FunctionModelBuilder,
)
from postcode.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)
from postcode.python_parser.model_builders.standalone_block_model_builder import (
    StandaloneBlockModelBuilder,
)

from postcode.models import (
    ImportModel,
    ParameterListModel,
    BlockType
)
from postcode.python_parser.visitors.base_code_block_visitor import BaseVisitor
import postcode.python_parser.visitors.node_processing.class_def_functions as class_def_functions
import postcode.python_parser.visitors.node_processing.function_def_functions as function_def_functions
import postcode.python_parser.visitors.node_processing.module_functions as module_functions
import postcode.python_parser.visitors.node_processing.standalone_code_block_functions as standalone_code_block_functions

from postcode.utilities.processing_context import (
    NodeAndPositionData,
    PositionData,
)
from postcode.python_parser.visitors.node_processing.gather_dependencies import (
    gather_and_set_children_dependencies,
)


class ModuleVisitor(BaseVisitor):
    """
    Visitor class for traversing and building a model of a Python module.

    This class extends BaseVisitor and is used to visit different nodes in a Python module's abstract
    syntax tree (CST) using the libcst library. It builds a structured model of the module, including
    imports, classes, and functions.

    Attributes:
        id (str): The ID of the module to be generated before instantiation.
        builder (ModuleModelBuilder): The builder used to construct the module model.

    Example:
        >>> module_builder = ModuleModelBuilder(id="module1", name="example_module")
        >>> visitor = ModuleVisitor(id="module1", module_builder=module_builder)
        >>> libcst.parse_module("import os\\nclass MyClass:\\n    pass").visit(visitor)
        # This will process the module and build its corresponding model using the provided module builder.
    """

    def __init__(self, id: str, module_builder: ModuleModelBuilder) -> None:
        super().__init__(id=id)
        self.builder: ModuleModelBuilder = module_builder
        self.builder_stack.append(module_builder)

    def visit_Module(self, node: libcst.Module) -> bool | None:
        """
        Visits the root Module node of the CST.

        Extracts various components of the module such as docstring, header, footer, and code content, and
        updates the module builder with these details.
        """

        docstring: str | None = node.get_docstring()
        header: list[str] = module_functions.extract_content_from_empty_lines(
            node.header
        )
        footer: list[str] = module_functions.extract_content_from_empty_lines(
            node.footer
        )
        content: str = node.code if node.code else ""
        position_data: PositionData = self.get_node_position_data(node)
        (
            self.builder.set_docstring(docstring)
            .set_header_content(header)
            .set_footer_content(footer)
            .set_code_content(content)
            .set_start_line_num(position_data.start)
            .set_end_line_num(position_data.end)
        )
        standalone_blocks: list[
            NodeAndPositionData
        ] = standalone_code_block_functions.gather_standalone_lines(node.body, self)
        standalone_block_models: list[
            StandaloneBlockModelBuilder
        ] = standalone_code_block_functions.process_standalone_blocks(
            code_blocks=standalone_blocks, parent_id=self.id
        )
        for standalone_block_model in standalone_block_models:
            self.builder.add_child(standalone_block_model)

    def visit_Import(self, node: libcst.Import) -> None:
        """
        Visits an Import node in the CST.

        Processes the import statement and updates the module builder with the import model.
        """

        import_model: ImportModel = module_functions.process_import(node)
        self.builder.add_import(import_model)

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        """
        Visits an ImportFrom node in the CST.

        Processes the 'from ... import ...' statement and updates the module builder with the import model.
        """

        import_model: ImportModel = module_functions.process_import_from(node)
        self.builder.add_import(import_model)

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        """
        Visits a ClassDef node in the CST.

        Initiates the process of building a class model from the class definition.
        """

        parent_id: str = self.builder_stack[-1].id
        class_id: str = ClassIDGenerationStrategy.generate_id(
            parent_id=parent_id, class_name=node.name.value
        )

        class_builder: ClassModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.CLASS,
            id=class_id,
            name=node.name.value,
            parent_id=parent_id,
        )

        builder = self.builder_stack[-1]
        builder.add_child(class_builder)
        self.builder_stack.append(class_builder)

        position_data: PositionData = self.get_node_position_data(node)
        class_def_functions.process_class_def(node, position_data, class_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        """
        Leaves a ClassDef node in the CST.

        Finalizes the class model building process by popping the current builder from the stack.
        """

        self.builder_stack.pop()

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        """
        Visits a FunctionDef node in the CST.

        Initiates the process of building a function model from the function definition.
        """

        parent_id: str = self.builder_stack[-1].id
        func_id: str = FunctionIDGenerationStrategy.generate_id(
            parent_id=parent_id, function_name=node.name.value
        )

        func_builder: FunctionModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.FUNCTION,
            id=func_id,
            name=node.name.value,
            parent_id=parent_id,
        )
        builder = self.builder_stack[-1]
        builder.add_child(func_builder)
        self.builder_stack.append(func_builder)

        position_data: PositionData = self.get_node_position_data(node)
        function_def_functions.process_func_def(
            func_id, node, position_data, func_builder
        )

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        """
        Visits a Parameters node in the CST.

        Processes the parameters of a function and updates the current function model builder with these parameters.
        """

        builder = self.builder_stack[-1]
        parameter_list: ParameterListModel | None = (
            function_def_functions.process_parameters(node)
        )

        if isinstance(builder, FunctionModelBuilder):
            builder.set_parameters_list(parameter_list)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        """
        Leaves a FunctionDef node in the CST.

        Finalizes the function model building process by popping the current builder from the stack.
        """

        self.builder_stack.pop()

    def leave_Module(self, original_node: libcst.Module) -> None:
        """
        Leaves the root Module node in the CST.

        Finalizes the module model building process by setting dependencies for children of the module.
        """

        gather_and_set_children_dependencies(self.builder)
