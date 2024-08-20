import json
from pydantic import BaseModel, Field, field_validator

from fenec.models.enums import (
    BlockType,
    ImportModuleType,
    CommentType,
)


class ImportNameModel(BaseModel):
    """Class representing the name of an import."""

    name: str
    as_name: str | None = None
    local_block_id: str | None = None

    @field_validator("as_name")
    def _check_as_name(cls, v) -> str:
        """Validates the as_name field."""
        if v is None:
            return ""
        else:
            return v

    @field_validator("local_block_id")
    def _check_local_block_id(cls, v) -> str:
        """Validates the local_block_id field."""
        if v is None:
            return ""
        else:
            return v


class ImportModel(BaseModel):
    """Class representing an import statement."""

    import_names: list[ImportNameModel]
    imported_from: str | None = None
    import_module_type: ImportModuleType = ImportModuleType.STANDARD_LIBRARY
    local_module_id: str | None = None

    @field_validator("imported_from")
    def _check_imported_from(cls, v) -> str:
        """Validates the imported_from field."""
        if v is None:
            return ""
        else:
            return v

    @field_validator("local_module_id")
    def _check_local_module_id(cls, v) -> str:
        """Validates the local_module_id field."""
        if v is None:
            return ""
        else:
            return v

    def _convert_import_to_metadata(self) -> str:
        """Converts the import to a metadata string."""
        return self.model_dump_json()


class DependencyModel(BaseModel):
    """Class representing a module dependency."""

    code_block_id: str

    def _convert_dependency_to_metadata(self) -> str:
        """Converts the dependency to a metadata string."""
        return self.model_dump_json()


class CommentModel(BaseModel):
    """Class representing a comment."""

    content: str
    comment_types: list[CommentType]

    def _convert_comment_to_metadata(self) -> str:
        """Converts the comment to a metadata string."""
        return self.model_dump_json()


class DecoratorModel(BaseModel):
    """Class representing a decorator."""

    content: str
    decorator_name: str
    decorator_args: list[str] | None = None

    @field_validator("decorator_args")
    def _check_decorator_args(cls, v) -> list[str]:
        """Validates the decorator_args field."""
        if v is None:
            return []
        else:
            return v

    def _convert_decorator_to_metadata(self) -> str:
        """Converts the decorator to a metadata string."""
        return self.model_dump_json()


class ClassKeywordModel(BaseModel):
    """Class representing a class keyword."""

    content: str
    keyword_name: str
    args: str | None = None

    @field_validator("args")
    def _check_args(cls, v) -> str:
        """Validates the args field."""
        if v is None:
            return ""
        else:
            return v

    def _convert_class_keyword_to_metadata(self) -> str:
        """Converts the class keyword to a metadata string."""
        return self.model_dump_json()


class ParameterListModel(BaseModel):
    """Class representing a list of parameters."""

    params: list[str] | None = None
    star_arg: str | None = None
    kwonly_params: list[str] | None = None
    star_kwarg: str | None = None
    posonly_params: list[str] | None = None

    @field_validator("params")
    def _check_params(cls, v) -> list[str]:
        """Validates the params field."""
        if v is None:
            return []
        else:
            return v

    @field_validator("star_arg")
    def _check_star_arg(cls, v) -> str:
        """Validates the star_arg field."""
        if v is None:
            # return ParameterModel(content="")
            return ""
        else:
            return v

    @field_validator("kwonly_params")
    def _check_kwonly_params(cls, v) -> list[str]:
        """Validates the kwonly_params field."""
        if v is None:
            return []
        else:
            return v

    @field_validator("star_kwarg")
    def _check_star_kwarg(cls, v) -> str:
        """Validates the star_kwarg field."""
        if v is None:
            # return ParameterModel(content="")
            return ""
        else:
            return v

    @field_validator("posonly_params")
    def _check_posonly_params(cls, v) -> list[str]:
        """Validates the posonly_params field."""
        if v is None:
            return []
        else:
            return v

    def _convert_parameters_to_metadata(self) -> str:
        """Converts the parameter list to a metadata string."""

        params: str = json.dumps(self.params, indent=4)
        kwonly_params: str = json.dumps(self.kwonly_params, indent=4)
        posonly_params: str = json.dumps(self.posonly_params, indent=4)
        return json.dumps(
            {
                "params": params,
                "star_arg": self.star_arg,
                "kwonly_params": kwonly_params,
                "star_kwarg": self.star_kwarg,
                "posonly_params": posonly_params,
            }
        )

    @classmethod
    def _build_parameter_list_model_from_metadata(
        cls, metadata: str
    ) -> "ParameterListModel":
        """Builds a parameter list model from metadata."""

        meta_data: dict = json.loads(metadata)
        params: list[str] = json.loads(meta_data["params"])
        star_arg: str = meta_data["star_arg"]
        kwonly_params: list[str] = json.loads(meta_data["kwonly_params"])
        star_kwarg: str = meta_data["star_kwarg"]
        posonly_params: list[str] = json.loads(meta_data["posonly_params"])

        return cls(
            params=params,
            star_arg=star_arg,
            kwonly_params=kwonly_params,
            star_kwarg=star_kwarg,
            posonly_params=posonly_params,
        )


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

    @field_validator("parent_id")
    def _check_parent_id(cls, v, values) -> str:
        """Validates that parent_id is a non-empty string unless block_type is MODULE."""
        block_type = (
            values.get("block_type")
            if isinstance(values, dict)
            else values.data.get("block_type")
        )

        if block_type and block_type != BlockType.MODULE:
            if v is None or len(v) < 1:
                raise ValueError(
                    "parent_id must be a non-empty string unless block_type is MODULE"
                )
        return v

    @field_validator("important_comments")
    def _check_important_comments(cls, v) -> list[CommentModel] | None:
        """Validates the important_comments field."""

        if v is None:
            return []
        else:
            return v

    @field_validator("dependencies")
    def _check_dependencies(cls, v) -> list[ImportModel | DependencyModel] | None:
        """Validates the dependencies field."""
        if v is None:
            return []
        else:
            return v

    @field_validator("summary")
    def _check_summary(cls, v) -> str:
        """Validates the summary field."""
        if v is None:
            return ""
        else:
            return v

    @field_validator("children_ids")
    def _check_children_ids(cls, v) -> list[str]:
        """Validates the children_ids field."""
        if v is None:
            return []
        else:
            return v

    def _convert_base_attributes_to_metadata(self) -> dict[str, str | int]:
        """Converts the base attributes to a metadata dictionary."""

        children_ids: str = json.dumps(self.children_ids, indent=4)
        dependencies: str = json.dumps(
            [
                (
                    dependency._convert_dependency_to_metadata()
                    if isinstance(dependency, DependencyModel)
                    else dependency._convert_import_to_metadata()
                )
                for dependency in self.dependencies  # type: ignore
            ],
            indent=4,
        )
        important_comments: str = json.dumps(
            [
                comment._convert_comment_to_metadata()
                for comment in self.important_comments  # type: ignore
            ],
            indent=4,
        )
        return {
            "id": self.id,
            "file_path": self.file_path,
            "parent_id": self.parent_id,  # type: ignore
            "block_type": self.block_type.name,
            "start_line_num": self.start_line_num,
            "end_line_num": self.end_line_num,
            "code_content": self.code_content,
            "important_comments": important_comments,
            "dependencies": dependencies,
            "summary": self.summary,
            "children_ids": children_ids,
        }

    @classmethod
    def _build_base_code_block_model_from_metadata(
        cls, metadata: dict
    ) -> "BaseCodeBlockModel":
        """Builds a base code block model from metadata."""

        important_comments: list[CommentModel] | None = []
        for comment in json.loads(metadata["important_comments"]):
            important_comments.append(CommentModel(**comment))
        if important_comments is []:
            important_comments = None

        dependencies: list[ImportModel | DependencyModel] | None = []
        for dependency_str in json.loads(metadata["dependencies"]):
            dependency = json.loads(dependency_str)
            if "import_names" in dependency:
                dependencies.append(ImportModel(**dependency))
            else:
                dependencies.append(DependencyModel(**dependency))
        if dependencies is []:
            dependencies = None

        children_ids: list[str] | None = json.loads(metadata["children_ids"])
        if children_ids is []:
            children_ids = None

        instance_dict = {
            "id": metadata["id"],
            "file_path": metadata["file_path"],
            "parent_id": metadata["parent_id"],
            "block_type": metadata["block_type"],
            "start_line_num": metadata["start_line_num"],
            "end_line_num": metadata["end_line_num"],
            "code_content": metadata["code_content"],
            "important_comments": important_comments,
            "dependencies": dependencies,
            "summary": metadata["summary"],
            "children_ids": children_ids,
        }
        return cls(**instance_dict)


class ModuleSpecificAttributes(BaseModel):
    """Module specific attributes."""

    docstring: str | None = None
    header: list[str] | None = None
    footer: list[str] | None = None
    imports: list[ImportModel] | None = None

    @field_validator("docstring")
    def _check_docstring(cls, v) -> str:
        """Validates the docstring field."""
        if v is None:
            return ""
        else:
            return v

    @field_validator("header")
    def _check_header(cls, v) -> list[str]:
        """Validates the header field."""
        if v is None:
            return []
        else:
            return v

    @field_validator("footer")
    def _check_footer(cls, v) -> list[str]:
        """Validates the footer field."""
        if v is None:
            return []
        else:
            return v

    @field_validator("imports")
    def _check_imports(cls, v) -> list[ImportModel]:
        """Validates the imports field."""
        if v is None:
            return []
        else:
            return v

    def _convert_module_attributes_to_metadata(self) -> dict[str, str | int]:
        """Converts the module attributes to a metadata dictionary."""

        header: str = json.dumps(self.header, indent=4)
        footer: str = json.dumps(self.footer, indent=4)
        imports: str = json.dumps([import_model._convert_import_to_metadata() for import_model in self.imports], indent=4)  # type: ignore
        return {
            "docstring": self.docstring,  # type: ignore
            "header": header,
            "footer": footer,
            "imports": imports,
        }

    @classmethod
    def _build_module_specific_attributes_from_metadata(
        cls, metadata: dict
    ) -> "ModuleSpecificAttributes":
        """Builds module specific attributes from metadata."""

        header: list[str] = json.loads(metadata["header"])
        footer: list[str] = json.loads(metadata["footer"])
        imports: list[ImportModel] = []
        for import_data in json.loads(metadata["imports"]):
            imports.append(ImportModel(**json.loads(import_data)))
        instance_dict = {
            "docstring": metadata["docstring"],
            "header": header,
            "footer": footer,
            "imports": imports,
        }
        return cls(**instance_dict)


class ModuleModel(BaseCodeBlockModel, ModuleSpecificAttributes):
    """
    Pydantic model for a module code block.

    Attributes:
        - `id` (str): The unique identifier for the module.
        - `file_path` (str): The path to the Python file that the module represents.
        - `parent_id` (str | None): The identifier of the parent (usually a directory).
        - `block_type` (BlockType): The type of code block that the module represents.
        - `start_line_num` (int): The line number of the first line of the module.
        - `end_line_num` (int): The line number of the last line of the module.
        - `code_content` (str): The string content of the module.
        - `important_comments` (list[CommentModel] | None): A list of important comments in the module.
        - `dependencies` (list[ImportModel | DependencyModel] | None): A list of dependencies for the module.
        - `summary` (str | None): A summary of the module.
        - `children_ids` (list[str] | None): A list of the identifiers of the children of the module.
        - `docstring` (str | None): The docstring of the module.
        - `header` (list[str] | None): The header of the module.
        - `footer` (list[str] | None): The footer of the module.
        - `imports` (list[ImportModel] | None): A list of import statements in the module.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the module model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata: dict) -> ModuleModel`
            - Builds a ModuleModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """
        Converts the module model to a metadata dictionary for ChromaDB.

        ChromaDB uses an extremely flat, JSON-like schema that only accepts simple types, [str | int | float | bool]. Thus this method
        flattens the module model's attributes and saves them in a dictionary to be stored in a ChromaDB collection.

        Returns:
            - `dict[str, str | int]`: A dictionary containing the module model's attributes.
        """
        return {
            **self._convert_base_attributes_to_metadata(),
            **self._convert_module_attributes_to_metadata(),
        }

    @classmethod
    def build_from_metadata(cls, metadata: dict) -> "ModuleModel":
        """
        Builds a ModuleModel from a metadata dictionary.

        This method uses the metadata dictionary from a ChromaDB collection to instantiate a ModuleModel object. It builds a
        `BaseCodeBlockModel` and a `ModuleSpecificAttributes` object from the metadata, combing them into a `ModuleModel` object.

        Args:
            - `metadata` (dict): A dictionary containing the metadata for the ModuleModel.

        Returns:
            - `ModuleModel`: A ModuleModel object with the attributes from the metadata dictionary.
        """

        base_code_block_model: BaseCodeBlockModel = (
            BaseCodeBlockModel._build_base_code_block_model_from_metadata(metadata)
        )
        module_specific_attributes: ModuleSpecificAttributes = (
            ModuleSpecificAttributes._build_module_specific_attributes_from_metadata(
                metadata
            )
        )
        return cls(
            **module_specific_attributes.model_dump(),
            **base_code_block_model.model_dump(),
        )


class ClassSpecificAttributes(BaseModel):
    """Class specific attributes."""

    class_name: str = Field(min_length=1)
    decorators: list[DecoratorModel] | None = None
    bases: list[str] | None = None
    docstring: str | None = None
    keywords: list[ClassKeywordModel] | None = None

    @field_validator("decorators")
    def _check_decorators(cls, v) -> list[DecoratorModel]:
        if v is None:
            return []
        else:
            return v

    @field_validator("bases")
    def _check_bases(cls, v) -> list[str]:
        if v is None:
            return []
        else:
            return v

    @field_validator("docstring")
    def _check_docstring(cls, v) -> str:
        if v is None:
            return ""
        else:
            return v

    @field_validator("keywords")
    def _check_keywords(cls, v) -> list[ClassKeywordModel]:
        if v is None:
            return []
        else:
            return v

    def _convert_class_attributes_to_metadata(self) -> dict[str, str]:
        decorators: str = json.dumps(
            [
                decorator._convert_decorator_to_metadata()
                for decorator in self.decorators  # type: ignore
            ],
            indent=4,
        )
        keywords: str = json.dumps(
            [
                keyword._convert_class_keyword_to_metadata()
                for keyword in self.keywords  # type: ignore
            ],
            indent=4,
        )
        bases: str = json.dumps(self.bases, indent=4)
        return {
            "class_name": self.class_name,
            "decorators": decorators,
            "bases": bases,
            "docstring": self.docstring if self.docstring else "",
            "keywords": keywords,
        }

    @classmethod
    def _build_class_specific_attributes_from_metadata(
        cls, metadata: dict
    ) -> "ClassSpecificAttributes":
        """Builds class specific attributes from metadata."""

        decorators: list[DecoratorModel] | None = []
        for decorator_data in json.loads(metadata["decorators"]):
            decorators.append(DecoratorModel(**json.loads(decorator_data)))
        if decorators is []:
            decorators = None

        keywords: list[ClassKeywordModel] | None = []
        for keyword_data in json.loads(metadata["keywords"]):
            keywords.append(ClassKeywordModel(**json.loads(keyword_data)))
        if keywords is []:
            keywords = None

        bases: list[str] = json.loads(metadata["bases"])
        docstring: str | None = metadata["docstring"] if metadata["docstring"] else None

        return cls(
            class_name=metadata["class_name"],
            decorators=decorators,
            bases=bases,
            docstring=docstring,
            keywords=keywords,
        )


class ClassModel(BaseCodeBlockModel, ClassSpecificAttributes):
    """
    Pydantic model for a class code block.

    Attributes:
        - `id` (str): The unique identifier for the class.
        - `file_path` (str): The path to the Python file that the class represents.
        - `parent_id` (str | None): The identifier of the parent (usually a module).
        - `block_type` (BlockType): The type of code block that the class represents.
        - `start_line_num` (int): The line number of the first line of the class.
        - `end_line_num` (int): The line number of the last line of the class.
        - `code_content` (str): The string content of the class.
        - `important_comments` (list[CommentModel] | None): A list of important comments in the class.
        - `dependencies` (list[ImportModel | DependencyModel] | None): A list of dependencies for the class.
        - `summary` (str | None): A summary of the class.
        - `children_ids` (list[str] | None): A list of the identifiers of the children of the class.
        - `class_name` (str): The name of the class.
        - `decorators` (list[DecoratorModel] | None): A list of decorators for the class.
        - `bases` (list[str] | None): A list of base classes for the class.
        - `docstring` (str | None): The docstring of the class.
        - `keywords` (list[ClassKeywordModel] | None): A list of keywords for the class.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the class model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata: dict) -> ClassModel`
            - Builds a ClassModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """
        Converts the class model to a metadata dictionary for ChromaDB.

        ChromaDB uses an extremely flat, JSON-like schema that only accepts simple types, [str | int | float | bool]. Thus this method
        flattens the class model's attributes and saves them in a dictionary to be stored in a ChromaDB collection.

        Returns:
            - `dict[str, str | int]`: A dictionary containing the class model's attributes.
        """

        return {
            **self._convert_base_attributes_to_metadata(),
            **self._convert_class_attributes_to_metadata(),
        }

    @classmethod
    def build_from_metadata(cls, metadata: dict) -> "ClassModel":
        """
        Builds a ClassModel from a metadata dictionary.

        This method uses the metadata dictionary from a ChromaDB collection to instantiate a ClassModel object. It builds a
        `BaseCodeBlockModel` and a `ClassSpecificAttributes` object from the metadata, combing them into a `ClassModel` object.

        Args:
            - `metadata` (dict): A dictionary containing the metadata for the ClassModel.

        Returns:
            - `ClassModel`: A ClassModel object with the attributes from the metadata dictionary.
        """

        class_specific_attributes: ClassSpecificAttributes = (
            ClassSpecificAttributes._build_class_specific_attributes_from_metadata(
                metadata
            )
        )
        base_code_block_model: BaseCodeBlockModel = (
            BaseCodeBlockModel._build_base_code_block_model_from_metadata(metadata)
        )
        return cls(
            **class_specific_attributes.model_dump(),
            **base_code_block_model.model_dump(),
        )


class FunctionSpecificAttributes(BaseModel):
    """Function specific attributes."""

    function_name: str = Field(min_length=1)
    docstring: str | None = None
    decorators: list[DecoratorModel] | None = None
    parameters: ParameterListModel | None = None
    returns: str | None = None
    is_method: bool = False
    is_async: bool = False

    @field_validator("docstring")
    def _check_docstring(cls, v) -> str:
        if v is None:
            return ""
        else:
            return v

    @field_validator("decorators")
    def _check_decorators(cls, v) -> list[DecoratorModel]:
        if v is None:
            return []
        else:
            return v

    @field_validator("parameters")
    def _check_parameters(cls, v) -> ParameterListModel:
        if v is None:
            return ParameterListModel(
                params=None,
                star_arg=None,
                kwonly_params=None,
                star_kwarg=None,
                posonly_params=None,
            )
        else:
            return v

    @field_validator("returns")
    def _check_returns(cls, v) -> str:
        if v is None:
            return ""
        else:
            return v

    def _convert_function_attributes_to_metadata(self) -> dict[str, str | int | bool]:
        """Converts the function attributes to a metadata dictionary for ChromaDB."""

        decorators: str = json.dumps(
            (
                [
                    decorator._convert_decorator_to_metadata()
                    for decorator in self.decorators  # type: ignore
                ]
            ),
            indent=4,
        )
        parameters: str = (
            self.parameters._convert_parameters_to_metadata() if self.parameters else ""
        )

        return {
            "function_name": self.function_name,
            "docstring": self.docstring if self.docstring else "",
            "decorators": decorators,
            "parameters": parameters,
            "returns": self.returns if self.returns else "",
            "is_method": self.is_method,
            "is_async": self.is_async,
        }

    @classmethod
    def _build_function_specific_attributes_from_metadata(
        cls, metadata: dict
    ) -> "FunctionSpecificAttributes":
        """Builds function specific attributes from metadata."""

        decorators: list[DecoratorModel] | None = []
        if metadata["decorators"]:
            for decorator_data in json.loads(metadata["decorators"]):
                decorators.append(DecoratorModel(**json.loads(decorator_data)))
            if decorators is []:
                decorators = None

        parameters: ParameterListModel | None = (
            ParameterListModel._build_parameter_list_model_from_metadata(
                metadata["parameters"]
            )
        )
        if parameters is None:
            parameters = None

        returns: str = metadata["returns"]

        return cls(
            function_name=metadata["function_name"],
            docstring=metadata["docstring"],
            decorators=decorators,
            parameters=parameters,
            returns=returns,
            is_method=metadata["is_method"],
            is_async=metadata["is_async"],
        )


class FunctionModel(BaseCodeBlockModel, FunctionSpecificAttributes):
    """
    Pydantic model for a function code block.

    Attributes:
        - `id` (str): The unique identifier for the function.
        - `file_path` (str): The path to the Python file that the function represents.
        - `parent_id` (str | None): The identifier of the parent (usually a module or class).
        - `block_type` (BlockType): The type of code block that the function represents.
        - `start_line_num` (int): The line number of the first line of the function.
        - `end_line_num` (int): The line number of the last line of the function.
        - `code_content` (str): The string content of the function.
        - `important_comments` (list[CommentModel] | None): A list of important comments in the function.
        - `dependencies` (list[ImportModel | DependencyModel] | None): A list of dependencies for the function.
        - `summary` (str | None): A summary of the function.
        - `children_ids` (list[str] | None): A list of the identifiers of the children of the function.
        - `function_name` (str): The name of the function.
        - `docstring` (str | None): The docstring of the function.
        - `decorators` (list[DecoratorModel] | None): A list of decorators for the function.
        - `parameters` (ParameterListModel | None): A model representing the function's parameters.
        - `returns` (str | None): A string representing the function's return annotation.
        - `is_method` (bool): True if the function is a method, False otherwise.
        - `is_async` (bool): True if the function is asynchronous, False otherwise.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the function model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata: dict) -> FunctionModel`
            - Builds a FunctionModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """
        Converts the function model to a metadata dictionary for ChromaDB.

        ChromaDB uses an extremely flat, JSON-like schema that only accepts simple types, [str | int | float | bool]. Thus this method
        flattens the function model's attributes and saves them in a dictionary to be stored in a ChromaDB collection.

        Returns:
            - `dict[str, str | int]`: A dictionary containing the function model's attributes.
        """

        return {
            **self._convert_base_attributes_to_metadata(),
            **self._convert_function_attributes_to_metadata(),
        }

    @classmethod
    def build_from_metadata(cls, metadata: dict) -> "FunctionModel":
        """
        Builds a FunctionModel from a metadata dictionary.

        This method uses the metadata dictionary from a ChromaDB collection to instantiate a FunctionModel object. It builds a
        `BaseCodeBlockModel` and a `FunctionSpecificAttributes` object from the metadata, combing them into a `FunctionModel` object.

        Args:
            - `metadata` (dict): A dictionary containing the metadata for the FunctionModel.

        Returns:
            - `FunctionModel`: A FunctionModel object with the attributes from the metadata dictionary.
        """

        function_specific_attributes: FunctionSpecificAttributes = (
            FunctionSpecificAttributes._build_function_specific_attributes_from_metadata(
                metadata
            )
        )
        base_code_block_model: BaseCodeBlockModel = (
            BaseCodeBlockModel._build_base_code_block_model_from_metadata(metadata)
        )
        return cls(
            **function_specific_attributes.model_dump(),
            **base_code_block_model.model_dump(),
        )


class StandaloneCodeBlockSpecificAttributes(BaseModel):
    """Standalone code block specific attributes."""

    variable_assignments: list[str] | None = None

    @field_validator("variable_assignments")
    def _check_variable_assignments(cls, v) -> list[str]:
        if v is None:
            return []
        else:
            return v

    def _convert_standalone_block_attributes_to_metadata(self) -> dict[str, str | int]:
        """Converts the standalone block attributes to a metadata dictionary."""
        return {
            "variable_assignments": json.dumps(self.variable_assignments, indent=4),
        }

    @classmethod
    def _build_standalone_block_specific_attributes_from_metadata(
        cls, metadata: dict
    ) -> "StandaloneCodeBlockSpecificAttributes":
        """Builds standalone block specific attributes from metadata."""
        variable_assignments: list[str] = json.loads(metadata["variable_assignments"])
        return cls(variable_assignments=variable_assignments)


class StandaloneCodeBlockModel(
    BaseCodeBlockModel, StandaloneCodeBlockSpecificAttributes
):
    """
    Model for a standalone code block.

    Attributes:
        - `id` (str): The unique identifier for the standalone code block.
        - `file_path` (str): The path to the Python file that the standalone code block represents.
        - `parent_id` (str | None): The identifier of the parent (usually a module or class).
        - `block_type` (BlockType): The type of code block that the standalone code block represents.
        - `start_line_num` (int): The line number of the first line of the standalone code block.
        - `end_line_num` (int): The line number of the last line of the standalone code block.
        - `code_content` (str): The string content of the standalone code block.
        - `important_comments` (list[CommentModel] | None): A list of important comments in the standalone code block.
        - `dependencies` (list[ImportModel | DependencyModel] | None): A list of dependencies for the standalone code block.
        - `summary` (str | None): A summary of the standalone code block.
        - `children_ids` (list[str] | None): A list of the identifiers of the children of the standalone code block.
        - `variable_assignments` (list[str] | None): A list of variable assignments in the standalone code block.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the standalone code block model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata: dict) -> StandaloneCodeBlockModel`
            - Builds a StandaloneCodeBlockModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """
        Converts the standalone code block model to a metadata dictionary for ChromaDB.

        ChromaDB uses an extremely flat, JSON-like schema that only accepts simple types, [str | int | float | bool]. Thus this method
        flattens the standalone code block model's attributes and saves them in a dictionary to be stored in a ChromaDB collection.

        Returns:
            - `dict[str, str | int]`: A dictionary containing the standalone code block model's attributes.
        """

        return {
            **self._convert_base_attributes_to_metadata(),
            **self._convert_standalone_block_attributes_to_metadata(),
        }

    @classmethod
    def build_from_metadata(cls, metadata: dict) -> "StandaloneCodeBlockModel":
        """
        Builds a StandaloneCodeBlockModel from a metadata dictionary.

        This method uses the metadata dictionary from a ChromaDB collection to instantiate a StandaloneCodeBlockModel object. It builds a
        `BaseCodeBlockModel` and a `StandaloneCodeBlockSpecificAttributes` object from the metadata, combing them into a `StandaloneCodeBlockModel` object.

        Args:
            - `metadata` (dict): A dictionary containing the metadata for the StandaloneCodeBlockModel.

        Returns:
            - `StandaloneCodeBlockModel`: A StandaloneCodeBlockModel object with the attributes from the metadata dictionary.
        """

        standalone_block_specific_attributes: StandaloneCodeBlockSpecificAttributes = (
            StandaloneCodeBlockSpecificAttributes._build_standalone_block_specific_attributes_from_metadata(
                metadata
            )
        )
        base_code_block_model: BaseCodeBlockModel = (
            BaseCodeBlockModel._build_base_code_block_model_from_metadata(metadata)
        )

        return cls(
            **standalone_block_specific_attributes.model_dump(),
            **base_code_block_model.model_dump(),
        )


class DirectoryModel(BaseModel):
    """
    Model for a directory.

    Attributes:
        - `id` (str): The unique identifier for the directory.
        - `block_type` (BlockType): The type of code block that the directory represents.
        - `directory_name` (str): The name of the directory.
        - `sub_directories_ids` (list[str]): A list of the identifiers of the sub-directories of the directory.
        - `children_ids` (list[str]): A list of the identifiers of the children of the directory.
        - `parent_id` (str | None): The identifier of the parent (usually a directory).
        - `summary` (str | None): A summary of the directory.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`:
            - Converts the directory model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata: dict) -> DirectoryModel`:
            - Builds a DirectoryModel from a metadata dictionary.
    """

    id: str
    block_type: BlockType = BlockType.DIRECTORY
    directory_name: str
    sub_directories_ids: list[str]
    children_ids: list[str]
    parent_id: str | None
    summary: str | None = None

    @field_validator("block_type")
    def _check_block_type(cls, v) -> str:
        if v != BlockType.DIRECTORY:
            raise ValueError("Block type must be DIRECTORY")
        return v

    @field_validator("parent_id")
    def _check_parent_id(cls, v) -> str:
        if v is None:
            return ""
        else:
            return v

    @field_validator("summary")
    def _check_summary(cls, v) -> str:
        if v is None:
            return ""
        else:
            return v

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the directory model to a metadata dictionary for ChromaDB."""

        sub_directories_ids: str = json.dumps(self.sub_directories_ids, indent=4)
        children_ids: str = json.dumps(self.children_ids, indent=4)
        return {
            "directory_name": self.directory_name,
            "sub_directories_ids": sub_directories_ids,
            "children_ids": children_ids,
            "parent_id": self.parent_id,  # type: ignore
            "summary": self.summary,
        }

    @classmethod
    def build_from_metadata(cls, metadata: dict) -> "DirectoryModel":
        sub_directories_ids: list[str] = json.loads(metadata["sub_directories_ids"])
        children_ids: list[str] = json.loads(metadata["children_ids"])

        return cls(
            id=metadata["id"],
            directory_name=metadata["directory_name"],
            sub_directories_ids=sub_directories_ids,
            children_ids=children_ids,
            parent_id=metadata["parent_id"],
            summary=metadata["summary"],
        )
