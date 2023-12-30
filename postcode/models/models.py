from typing import Union
from pydantic import BaseModel, Field, validator

from postcode.models.enums import (
    BlockType,
    ImportModuleType,
    CommentType,
)


class ImportNameModel(BaseModel):
    """Class representing the name of an import."""

    name: str
    as_name: str | None = None
    local_block_id: str | None = None

    # def convert_import_names_to_metadata(self) -> str:
    #     """Converts the import name to a metadata string."""

    #     return self.model_dump_json()


class ImportModel(BaseModel):
    """Class representing an import statement."""

    import_names: list[ImportNameModel]
    imported_from: str | None = None
    import_module_type: ImportModuleType = ImportModuleType.STANDARD_LIBRARY
    local_module_id: str | None = None

    def convert_import_to_metadata(self) -> str:
        """Converts the import to a metadata string."""
        return self.model_dump_json()


class DependencyModel(BaseModel):
    """Class representing a module dependency."""

    code_block_id: str

    def convert_dependency_to_metadata(self) -> str:
        """Converts the dependency to a metadata string."""
        return self.model_dump_json()


class CommentModel(BaseModel):
    """Class representing a comment."""

    content: str
    comment_types: list[CommentType]

    def convert_comment_to_metadata(self) -> str:
        """Converts the comment to a metadata string."""
        return self.model_dump_json()


class DecoratorModel(BaseModel):
    """Class representing a decorator."""

    content: str
    decorator_name: str
    decorator_args: list[str] | None = None

    def convert_decorator_to_metadata(self) -> str:
        """Converts the decorator to a metadata string."""
        return self.model_dump_json()


class ClassKeywordModel(BaseModel):
    """Class representing a class keyword."""

    content: str
    keyword_name: str
    args: str | None = None

    def convert_class_keyword_to_metadata(self) -> str:
        """Converts the class keyword to a metadata string."""
        return self.model_dump_json()


class ParameterModel(BaseModel):
    """Class representing a function parameter."""

    content: str


class ParameterListModel(BaseModel):
    """Class representing a list of parameters."""

    params: list[ParameterModel] | None = None
    star_arg: ParameterModel | None = None
    kwonly_params: list[ParameterModel] | None = None
    star_kwarg: ParameterModel | None = None
    posonly_params: list[ParameterModel] | None = None

    def convert_parameters_to_metadata(self) -> str:
        """Converts the parameter list to a metadata string."""
        return self.model_dump_json()


class BaseCodeBlockModel(BaseModel):
    """Attributes common to all code block models."""

    id: str
    file_path: str = Field(min_length=1)
    parent_id: str | None = None
    block_type: BlockType
    start_line_num: int
    end_line_num: int
    code_content: str = ""
    important_comments: list[CommentModel] | None = None
    dependencies: list[ImportModel | DependencyModel] | None = None
    summary: str | None = None
    children_ids: list[str] | None = []

    @validator("parent_id", always=True)
    def check_parent_id(cls, v, values, **kwargs) -> str | None:
        """Validates that parent_id is a non-empty string unless block_type is MODULE."""

        if "block_type" in values and values["block_type"] != BlockType.MODULE:
            if len(v) < 1:
                raise ValueError("parent_id is required!")
        return v

    def _convert_parent_id_to_metadata(self) -> str:
        """Converts the parent_id to a metadata string."""
        return f"{self.parent_id}" if self.parent_id else ""

    def _convert_block_type_to_metadata(self) -> str:
        """Converts the block_type to a metadata string."""
        return f"{self.block_type.name}"

    def _convert_important_comments_to_metadata(self) -> str:
        """Converts the important comments to a metadata string."""

        important_comments: str = (
            self.model_dump_json() if self.important_comments else ""
        )

        return f"{important_comments}"

    def _convert_dependencies_to_metadata(self) -> str:
        """Converts the dependencies to a metadata string."""

        dependencies_str: str = ""

        if self.dependencies:
            for dependency in self.dependencies:
                if isinstance(dependency, ImportModel):
                    dependencies_str += f"{dependency.convert_import_to_metadata()}\n"
                elif isinstance(dependency, DependencyModel):
                    dependencies_str += (
                        f"{dependency.convert_dependency_to_metadata()}\n"
                    )

        return dependencies_str

    def _convert_summary_to_metadata(self) -> str:
        """Converts the summary to a metadata string."""
        return f"{self.summary}" if self.summary else ""

    def _convert_children_to_metadata(self) -> str:
        """Converts the children to a metadata string."""

        return str(self.children_ids) if self.children_ids else ""

    def _convert_base_attributes_to_metadata_dict(self) -> dict[str, str | int]:
        """Converts the base attributes to a metadata dictionary."""

        return {
            "id": self.id,
            "file_path": self.file_path,
            "parent_id": self._convert_parent_id_to_metadata(),
            "block_type": self._convert_block_type_to_metadata(),
            "start_line_num": self.start_line_num,
            "end_line_num": self.end_line_num,
            "code_content": self.code_content,
            "important_comments": self._convert_important_comments_to_metadata(),
            "dependencies": self._convert_dependencies_to_metadata(),
            "summary": self._convert_summary_to_metadata(),
            "children": self._convert_children_to_metadata(),
        }


class ModuleSpecificAttributes(BaseModel):
    """Module specific attributes."""

    docstring: str | None = None
    header: list[str] | None = None
    footer: list[str] | None = None
    imports: list[ImportModel] | None = None

    def _convert_docstring_to_metadata(self) -> str:
        """Converts the docstring to a metadata string."""
        return f"{self.docstring}"

    def _convert_header_to_metadata(self) -> str:
        """Converts the header and footer to a metadata string."""
        return self.model_dump_json()

    def _convert_footer_to_metadata(self) -> str:
        """Converts the header and footer to a metadata string."""
        return self.model_dump_json()

    def _convert_imports_to_metadata(self) -> str:
        """Converts the imports to a metadata string."""
        imports_str: str = self.model_dump_json() if self.imports else ""
        return f"{imports_str}"

    def _convert_module_attributes_to_metadata_dict(self) -> dict[str, str | int]:
        """Converts the module attributes to a metadata dictionary."""

        return {
            "docstring": self._convert_docstring_to_metadata(),
            "header": self._convert_header_to_metadata(),
            "footer": self._convert_footer_to_metadata(),
            "imports": self._convert_imports_to_metadata(),
        }


class ModuleModel(BaseCodeBlockModel, ModuleSpecificAttributes):
    """Model for a module."""

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the module model to a metadata dictionary."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_module_attributes_to_metadata_dict(),
        }


class ClassSpecificAttributes(BaseModel):
    """Class specific attributes."""

    class_name: str = Field(min_length=1)
    decorators: list[DecoratorModel] | None = None
    bases: list[str] | None = None
    docstring: str | None = None
    keywords: list[ClassKeywordModel] | None = None
    # attributes: list[dict] | None = None

    def _convert_decorators_to_metadata(self) -> str:
        """Converts the decorators to a metadata string."""
        decorators_str: str = self.model_dump_json() if self.decorators else ""
        return f"{decorators_str}"

    def _convert_bases_to_metadata(self) -> str:
        """Converts the bases to a metadata string."""
        return self.model_dump_json() if self.bases else ""

    def _convert_docstring_to_metadata(self) -> str:
        """Converts the docstring to a metadata string."""
        return f"{self.docstring}" if self.docstring else ""

    def _convert_keywords_to_metadata(self) -> str:
        """Converts the keywords to a metadata string."""
        keywords_str: str = self.model_dump_json() if self.keywords else ""
        return f"{keywords_str}"

    def _convert_class_attributes_to_metadata_dict(self) -> dict[str, str | int]:
        """Converts the class attributes to a metadata dictionary."""

        return {
            "class_name": self.class_name,
            "decorators": self._convert_decorators_to_metadata(),
            "bases": self._convert_bases_to_metadata(),
            "docstring": self._convert_docstring_to_metadata(),
            "keywords": self._convert_keywords_to_metadata(),
        }


class ClassModel(BaseCodeBlockModel, ClassSpecificAttributes):
    """Model for a class."""

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the class model to a metadata dictionary."""
        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_class_attributes_to_metadata_dict(),
        }


class FunctionSpecificAttributes(BaseModel):
    """Function specific attributes."""

    function_name: str = Field(min_length=1)
    docstring: str | None = None
    decorators: list[DecoratorModel] | None = None
    parameters: ParameterListModel | None = None
    returns: str | None = None
    is_method: bool = False
    is_async: bool = False

    def _convert_docstring_to_metadata(self) -> str:
        """Converts the docstring to a metadata string."""
        return f"{self.docstring}" if self.docstring else ""

    def _convert_decorators_to_metadata(self) -> str:
        """Converts the decorators to a metadata string."""
        decorators_str: str = self.model_dump_json() if self.decorators else ""
        return f"{decorators_str}"

    def _convert_parameters_to_metadata(self) -> str:
        """Converts the parameters to a metadata string."""
        return (
            self.parameters.convert_parameters_to_metadata() if self.parameters else ""
        )

    def _convert_returns_to_metadata(self) -> str:
        """Converts the returns to a metadata string."""
        return f"{self.returns}" if self.returns else ""

    def _convert_function_attributes_to_metadata_dict(self) -> dict[str, str | bool]:
        """Converts the function attributes to a metadata dictionary."""

        return {
            "function_name": self.function_name,
            "docstring": self._convert_docstring_to_metadata(),
            "decorators": self._convert_decorators_to_metadata(),
            "parameters": self._convert_parameters_to_metadata(),
            "returns": self._convert_returns_to_metadata(),
            "is_method": self.is_method,
            "is_async": self.is_async,
        }


class FunctionModel(BaseCodeBlockModel, FunctionSpecificAttributes):
    """Model for a function."""

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the function model to a metadata dictionary."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_function_attributes_to_metadata_dict(),
        }


class StandaloneCodeBlockSpecificAttributes(BaseModel):
    """Standalone code block specific attributes."""

    variable_assignments: list[str] | None = None

    def _convert_variable_assignments_to_metadata(self) -> str:
        """Converts the variable assignments to a metadata string."""
        return self.model_dump_json() if self.variable_assignments else ""

    def _convert_standalone_block_attributes_to_metadata_dict(
        self,
    ) -> dict[str, str | int]:
        """Converts the standalone code block attributes to a metadata dictionary."""
        return {
            "variable_assignments": self._convert_variable_assignments_to_metadata(),
        }


class StandaloneCodeBlockModel(
    BaseCodeBlockModel, StandaloneCodeBlockSpecificAttributes
):
    """Model for a standalone code block."""

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the standalone code block model to a metadata dictionary."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_standalone_block_attributes_to_metadata_dict(),
        }


class DirectoryModel(BaseModel):
    """Model for a directory."""

    id: str
    block_type: BlockType = BlockType.DIRECTORY
    directory_name: str
    sub_directories_ids: list[str]
    module_ids: list[str]
    summary: str | None = None

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the directory model to a metadata dictionary."""

        return {
            "directory_name": self.directory_name,
            "sub_directories": str(self.sub_directories_ids)
            if self.sub_directories_ids
            else "",
            "module_ids": self.model_dump_json() if self.module_ids else "",
            "summary": self.summary if self.summary else "",
        }
