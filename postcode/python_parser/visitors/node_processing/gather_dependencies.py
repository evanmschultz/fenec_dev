import re
from typing import Callable, Sequence

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
from postcode.python_parser.models.models import ImportModel, DependencyModel


def gather_and_set_children_dependencies(module_builder: ModuleModelBuilder) -> None:
    """
    Gathers and sets dependencies for each child code block in the module.

    This function iterates over each child builder of the module builder, gathers import and non-import dependencies,
    and sets these dependencies for each block.

    Args:
        module_builder (ModuleModelBuilder): A builder object representing the entire module.

    Example:
        module_builder = ModuleModelBuilder(...)  # initialize with necessary parameters
        gather_and_set_children_dependencies(module_builder)
        # After execution, each child block builder of the module_builder will have its dependencies set.
    """

    for block_builder in module_builder.children_builders:
        block_dependencies: list[ImportModel | DependencyModel] = []
        code_content: str = block_builder.common_attributes.code_content

        import_dependencies: list[ImportModel] = _gather_import_dependencies(
            module_builder.module_attributes.imports, code_content
        )
        block_dependencies.extend(import_dependencies)

        non_import_dependencies: list[
            DependencyModel
        ] = _gather_non_import_dependencies(
            module_builder.children_builders,
            block_builder,
            code_content,
            _create_module_dependency_model,
        )
        block_dependencies.extend(non_import_dependencies)

        block_builder.set_dependencies(block_dependencies)


def _gather_import_dependencies(
    imports: list[ImportModel] | None, code_content: str
) -> list[ImportModel]:
    """
    Gathers import dependencies from the provided code content.

    This function checks for the presence of import names (and their aliases) in the given code content
    and returns a list of import models that are dependencies for the code block.

    Args:
        imports (list[ImportModel] | None): A list of import models to check against the code content.
        code_content (str): The string content of the code block being analyzed.

    Returns:
        list[ImportModel]: A list of import models that the code content depends on.
    """

    block_dependencies: list[ImportModel] = []

    if imports:
        for import_model in imports:
            for import_name_model in import_model.import_names:
                if import_name_model.as_name:
                    if import_name_model.as_name in code_content:
                        block_dependencies.append(import_model)

                if import_name_model.name in code_content:
                    block_dependencies.append(import_model)

    return block_dependencies


def _get_standalone_block_dependency(
    builder: StandaloneBlockModelBuilder,
    code_content: str,
    dependency_creator: Callable[[str], DependencyModel],
) -> DependencyModel | None:
    """
    Identifies if the given standalone block is a dependency based on variable usage.

    This function checks if any of the variable assignments in the standalone block are used in the given code content.
    If so, it returns the ID of the standalone block builder.

    Args:
        builder (StandaloneBlockModelBuilder): The standalone block builder to check for dependencies.
        code_content (str): The code content to analyze for variable usage.

    Returns:
        str | None: The ID of the standalone block builder if a dependency is found, otherwise None.
    """

    variables: list[
        str
    ] | None = builder.standalone_block_attributes.variable_assignments
    if variables:
        for variable in variables:
            if re.search(rf"\b{variable}\b\s*=", code_content) is None and re.search(
                rf"\b{variable}\b", code_content
            ):
                return dependency_creator(builder.id)


def _gather_standalone_block_dependency_for_standalone_block(
    builder: StandaloneBlockModelBuilder,
    code_content: str,
    dependency_creator: Callable[[str], DependencyModel],
) -> DependencyModel | None:
    """
    Determines if a given standalone block is a dependency for another standalone block.

    This function checks if any of the variable assignments in the provided standalone block
    are present in the given code content of another standalone block.

    Args:
        builder (StandaloneBlockModelBuilder): The standalone block builder to check for dependencies.
        code_content (str): The code content of another standalone block to analyze.

    Returns:
        str | None: The ID of the standalone block builder if a dependency is found, otherwise None.
    """

    variables: list[
        str
    ] | None = builder.standalone_block_attributes.variable_assignments
    if variables:
        for variable in variables:
            if variable in code_content:
                return dependency_creator(builder.id)


def _not_same_builder(
    builder: ClassModelBuilder | FunctionModelBuilder | StandaloneBlockModelBuilder,
    block_builder: ClassModelBuilder
    | FunctionModelBuilder
    | StandaloneBlockModelBuilder,
) -> bool:
    """Checks if the given builders are not the same, returning boolean."""
    return builder != block_builder


def _gather_non_import_dependencies(
    children_builders: Sequence[
        ClassModelBuilder | FunctionModelBuilder | StandaloneBlockModelBuilder
    ],
    block_builder: ClassModelBuilder
    | FunctionModelBuilder
    | StandaloneBlockModelBuilder,
    code_content: str,
    dependency_creator: Callable[[str], DependencyModel],
) -> list[DependencyModel]:
    """
    Gather non-import dependencies from the given `children_builders` and `block_builder`
    based on the provided `code_content`.

    Args:
        children_builders (list): List of builders representing child nodes.
        block_builder: Builder representing the current block.
        code_content (str): Content of the code.

    Returns:
        list: List of dependencies.
    """

    block_dependencies: list[DependencyModel] = []
    for builder in children_builders:
        if _not_same_builder(builder, block_builder):
            if isinstance(builder, ClassModelBuilder):
                if builder.class_attributes.class_name in code_content:
                    module_dependency = dependency_creator(builder.id)
                    block_dependencies.append(module_dependency)

            elif isinstance(builder, FunctionModelBuilder):
                if builder.function_attributes.function_name in code_content:
                    module_dependency = dependency_creator(builder.id)
                    block_dependencies.append(module_dependency)

            elif isinstance(builder, StandaloneBlockModelBuilder) and isinstance(
                block_builder, StandaloneBlockModelBuilder
            ):
                module_dependency: DependencyModel | None = (
                    _gather_standalone_block_dependency_for_standalone_block(
                        builder, code_content, dependency_creator
                    )
                )
                if module_dependency:
                    block_dependencies.append(module_dependency)

            # TODO: Improve logic to find variable dependencies
            elif isinstance(builder, StandaloneBlockModelBuilder):
                module_dependency = _get_standalone_block_dependency(
                    builder, code_content, dependency_creator
                )
                if module_dependency:
                    block_dependencies.append(module_dependency)

    return block_dependencies


def _create_module_dependency_model(module_code_block_id: str) -> DependencyModel:
    return DependencyModel(code_block_id=module_code_block_id)
