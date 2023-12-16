from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union
from abc import ABC, abstractmethod

from postcode.python_parser.models.models import (
    BaseCodeBlockModel,
    CommentModel,
    ImportModel,
    DependencyModel,
)

from postcode.python_parser.models.enums import BlockType

if TYPE_CHECKING:
    from postcode.python_parser.model_builders.class_model_builder import (
        ClassModelBuilder,
    )
    from postcode.python_parser.model_builders.function_model_builder import (
        FunctionModelBuilder,
    )
    from postcode.python_parser.model_builders.module_model_builder import (
        ModuleModelBuilder,
    )
    from postcode.python_parser.model_builders.standalone_block_model_builder import (
        StandaloneBlockModelBuilder,
    )


class BaseModelBuilder(ABC):
    """
    Abstract base class for building models of different code blocks.

    This class follows the builder pattern, providing a structured approach to constructing models for various types of code blocks (like modules, classes, functions). It defines common attributes and methods used across all specific model builders.

    Attributes:
        id (str): The unique identifier for the code block.
        children_builders (list[Union[ClassModelBuilder, FunctionModelBuilder, StandaloneBlockModelBuilder]]):
            A list of builders for the children code blocks.
        common_attributes (BaseCodeBlockModel): An instance containing common attributes shared across different code block models.

    Example:
        # This example demonstrates how a derived builder might be initialized and used.
        >>> class SomeModelBuilder(BaseModelBuilder):
                def build(self):
                    # Building logic specific to 'SomeModelBuilder'
                    pass
        >>> builder = SomeModelBuilder(id='123', block_type=BlockType.CLASS, parent_id='root')
        >>> builder.set_start_line_num(1).set_end_line_num(10)
        # Sets the start and end line numbers for the code block.
    """

    def __init__(
        self, *, id: str, block_type: BlockType, parent_id: str | None
    ) -> None:
        self.id: str = id
        self.children_builders: list[
            ClassModelBuilder | FunctionModelBuilder | StandaloneBlockModelBuilder
        ] = []

        self.common_attributes = BaseCodeBlockModel(
            id=id,
            parent_id=parent_id,
            block_type=block_type,
            start_line_num=0,
            end_line_num=0,
            code_content="",
            important_comments=None,
            children=None,
            dependencies=None,
            summary=None,
        )

    def set_start_line_num(
        self, line_num: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the start line number of the code block model instance."""
        self.common_attributes.start_line_num = line_num
        return self

    def set_end_line_num(
        self, line_num: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the end line number of the code block model instance."""
        self.common_attributes.end_line_num = line_num
        return self

    def set_code_content(
        self, code_content: str
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds the string containing the content of the code block to the model instance."""
        self.common_attributes.code_content = code_content
        return self

    def add_important_comment(
        self, comment: CommentModel
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds an important comment to the model instance."""
        if not self.common_attributes.important_comments:
            self.common_attributes.important_comments = []
        self.common_attributes.important_comments.append(comment)
        return self

    def add_summary(
        self, summary: str
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a summary to the model instance."""
        self.common_attributes.summary = summary
        # print(f"Added summary to {self.common_attributes.id}")
        return self

    def add_child(
        self,
        child: Union[
            "ClassModelBuilder", "FunctionModelBuilder", StandaloneBlockModelBuilder
        ],
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a child code block to the model instance."""
        self.children_builders.append(child)
        return self

    def set_dependencies(
        self, dependencies: list[ImportModel | DependencyModel] | None
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the dependencies of the model instance."""
        self.common_attributes.dependencies = dependencies
        return self

    def update_import_dependency(
        self,
        new_import_model: ImportModel,
        old_import_model: ImportModel,
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """
        Updates an import in the model instance.

        Args:
            new_import_model (ImportModel): The updated import model.
            old_import_model

        Returns:
            BaseModelBuilder: The base model builder instance.
        """

        if self.common_attributes.dependencies:
            import_model_to_remove: ImportModel | None = None
            for existing_import_model in self.common_attributes.dependencies:
                if isinstance(existing_import_model, DependencyModel):
                    continue

                if (
                    existing_import_model.import_names == old_import_model.import_names
                    and existing_import_model.imported_from
                    == old_import_model.imported_from
                    and existing_import_model.import_module_type
                    == old_import_model.import_module_type
                ):
                    import_model_to_remove = existing_import_model
                    break

            if not import_model_to_remove:
                raise Exception(f"Could not find import to remove: {old_import_model}")

            self.common_attributes.dependencies.remove(import_model_to_remove)
            self.common_attributes.dependencies.append(new_import_model)
        else:
            raise Exception(
                f"No imports in the builders imports list: {self.common_attributes.dependencies}"
            )
        return self

    def build_and_set_children(self) -> None:
        if self.children_builders:
            self.common_attributes.children = [
                child.build() for child in self.children_builders
            ]

    def _get_common_attributes(self) -> dict[str, Any]:
        """
        Returns a dictionary containing the attributes common to all code block models.
        """
        return self.common_attributes.model_dump()

    @abstractmethod
    def build(
        self,
    ) -> None:
        """
        Builds and returns the code block model instance.

        Returns:
            CodeBlockModel: The built code block model instance.
        """
        ...
