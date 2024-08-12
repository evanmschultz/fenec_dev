import logging
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

    @classmethod
    def _build_from_metadata(cls, metadata: dict[str, str]) -> "ImportNameModel":
        """
        Builds an ImportNameModel from a metadata dictionary.

        Args:
            metadata (dict[str, str]): A dictionary containing metadata for an import name.

        Returns:
            ImportNameModel: An instance of ImportNameModel.
        """
        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            name: str | None = metadata.get("name")
            if not name:
                raise ValueError("Import name must be a string.")

            return cls(
                name=name,
                as_name=metadata.get("as_name"),
                local_block_id=metadata.get("local_block_id"),
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class ImportModel(BaseModel):
    """Class representing an import statement."""

    import_names: list[ImportNameModel]
    imported_from: str | None = None
    import_module_type: ImportModuleType = ImportModuleType.STANDARD_LIBRARY
    local_module_id: str | None = None

    def convert_import_to_metadata(self) -> str:
        """Converts the import to a metadata string."""
        return self.model_dump_json()

    @classmethod
    def _build_from_metadata(
        cls, metadata: dict[str, str | list[dict[str, str]]]
    ) -> "ImportModel":
        """
        Builds an ImportModel from a metadata dictionary.

        Args:
            metadata (dict): A dictionary containing metadata for an import statement.

        Returns:
            ImportModel: An instance of ImportModel.
        """
        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            import_names_data = metadata.get("import_names", [])
            if not isinstance(import_names_data, list):
                raise ValueError("import_names must be a list.")

            import_names = [
                ImportNameModel._build_from_metadata(name) for name in import_names_data
            ]

            import_from = metadata.get("imported_from")

            if not isinstance(import_from, str):
                raise ValueError("imported_from must be a string.")

            if import_from == "":
                import_from = None

            import_module_type_raw = metadata.get("import_module_type")
            if not isinstance(import_module_type_raw, str):
                raise ValueError("import_module_type must be a string.")

            try:
                import_module_type = ImportModuleType(metadata["import_module_type"])
            except ValueError:
                raise ValueError("Invalid import module type.")

            local_module_id = metadata.get("local_module_id")
            if not isinstance(local_module_id, str):
                raise ValueError("local_module_id must be a string.")

            if not local_module_id:
                raise ValueError("local_module_id cannot be empty.")

            return cls(
                import_names=import_names,
                imported_from=import_from,
                import_module_type=import_module_type,
                local_module_id=local_module_id,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class DependencyModel(BaseModel):
    """Class representing a module dependency."""

    code_block_id: str

    def convert_dependency_to_metadata(self) -> str:
        """Converts the dependency to a metadata string."""
        return self.model_dump_json()

    @classmethod
    def _build_from_metadata(cls, metadata: dict[str, str]) -> "DependencyModel":
        """Builds a DependencyModel from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            return cls(
                code_block_id=metadata["code_block_id"],
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class CommentModel(BaseModel):
    """Class representing a comment."""

    content: str
    comment_types: list[CommentType]

    def convert_comment_to_metadata(self) -> str:
        """Converts the comment to a metadata string."""
        return self.model_dump_json()

    @classmethod
    def _build_from_metadata(
        cls, metadata: dict[str, str | list[str]]
    ) -> "CommentModel":
        """Builds a CommentModel from a metadata dictionary."""
        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            content = metadata.get("content", "")
            if not isinstance(content, str):
                raise ValueError("Content must be a string.")

            comment_types_raw = metadata.get("comment_types", [])
            if not isinstance(comment_types_raw, list):
                raise ValueError("Comment types must be a list.")

            comment_types: list[CommentType] = []
            for comment_type_str in comment_types_raw:
                try:
                    comment_type = CommentType(comment_type_str)
                    comment_types.append(comment_type)
                except ValueError:
                    raise ValueError(f"Invalid comment type: {comment_type_str}")

            return cls(content=content, comment_types=comment_types)
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise


class DecoratorModel(BaseModel):
    """Class representing a decorator."""

    content: str
    decorator_name: str
    decorator_args: list[str] | None = None

    def convert_decorator_to_metadata(self) -> str:
        """Converts the decorator to a metadata string."""
        return self.model_dump_json()

    @classmethod
    def _build_from_metadata(
        cls, metadata: dict[str, str | list[str] | None]
    ) -> "DecoratorModel":
        """Builds a DecoratorModel from a metadata dictionary."""
        try:
            # Ensure the metadata is a dictionary
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            content = metadata.get("content", "")
            decorator_name = metadata.get("decorator_name", "")

            if not isinstance(decorator_name, str) and not isinstance(content, str):
                raise ValueError("Decorator name and content must be strings.")

            # Handle decorator_args, ensuring it's a list[str] or None
            decorator_args_raw = metadata.get("decorator_args")
            decorator_args = None  # Default to None
            if isinstance(decorator_args_raw, list):
                # If it's a list, ensure all elements are strings
                if all(isinstance(arg, str) for arg in decorator_args_raw):
                    decorator_args = decorator_args_raw
                else:
                    raise ValueError("All decorator arguments must be strings.")
            elif isinstance(decorator_args_raw, str):
                # If it's a string, wrap it in a list
                decorator_args = [decorator_args_raw]
            elif decorator_args_raw is not None:
                # If it's not a list, string, or None, it's an invalid type
                raise ValueError(
                    "Decorator arguments must be a string, a list of strings, or None."
                )

            return cls(content=content, decorator_name=decorator_name, decorator_args=decorator_args)  # type: ignore # FIXME: fix type hinting error
        except ValueError as ve:
            print(f"Error building from metadata: {ve}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise


class ClassKeywordModel(BaseModel):
    """Class representing a class keyword."""

    content: str
    keyword_name: str
    args: str | None = None

    def convert_class_keyword_to_metadata(self) -> str:
        """Converts the class keyword to a metadata string."""
        return self.model_dump_json()

    @classmethod
    def _build_from_metadata(cls, metadata: dict[str, str]) -> "ClassKeywordModel":
        """Builds a ClassKeywordModel from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            return cls(
                content=metadata["content"],
                keyword_name=metadata["keyword_name"],
                args=metadata["args"] if "args" in metadata else None,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


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

    @classmethod
    def _build_from_metadata(cls, metadata: dict[str, str]) -> "ParameterListModel":
        """Builds a ParameterListModel from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            params: list[ParameterModel] | None = (
                [ParameterModel(content=param) for param in metadata.get("params", [])]
                if "params" in metadata and isinstance(metadata["params"], list)
                else None
            )
            star_arg: ParameterModel | None = (
                ParameterModel(content=metadata["star_arg"])
                if "star_arg" in metadata and isinstance(metadata["star_arg"], str)
                else None
            )
            kwonly_params: list[ParameterModel] | None = (
                [
                    ParameterModel(content=param)
                    for param in metadata.get("kwonly_params", [])
                ]
                if "kwonly_params" in metadata
                and isinstance(metadata["kwonly_params"], list)
                else None
            )
            star_kwarg: ParameterModel | None = (
                ParameterModel(content=metadata["star_kwarg"])
                if "star_kwarg" in metadata and isinstance(metadata["star_kwarg"], str)
                else None
            )
            posonly_params: list[ParameterModel] | None = (
                [
                    ParameterModel(content=param)
                    for param in metadata.get("posonly_params", [])
                ]
                if "posonly_params" in metadata
                and isinstance(metadata["posonly_params"], list)
                else None
            )

            return cls(
                params=params,
                star_arg=star_arg,
                kwonly_params=kwonly_params,
                star_kwarg=star_kwarg,
                posonly_params=posonly_params,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


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
    def check_parent_id(cls, v, values) -> str | None:
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
        """Converts the base attributes to a metadata dictionary for ChromaDB."""

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

    @classmethod
    def _build_from_metadata(
        cls, metadata: dict[str, str | int | list[str]]
    ) -> "BaseCodeBlockModel":
        """Builds a BaseCodeBlockModel from a metadata dictionary."""
        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            id = metadata.get("id")
            if not isinstance(id, str):
                raise ValueError("ID must be a string.")

            file_path = metadata.get("file_path")
            if not isinstance(file_path, str):
                raise ValueError("File path must be a string.")

            block_type = metadata.get("block_type")
            if (
                not isinstance(block_type, str)
                or block_type not in BlockType._member_names_
            ):
                raise ValueError("Invalid block type.")

            start_line_num = metadata.get("start_line_num")
            if not isinstance(start_line_num, int):
                raise ValueError("Start line number must be an integer.")

            end_line_num = metadata.get("end_line_num")
            if not isinstance(end_line_num, int):
                raise ValueError("End line number must be an integer.")

            parent_id = metadata.get("parent_id")
            if not isinstance(parent_id, str):
                raise ValueError("Parent ID must be a string.")

            code_content = metadata.get("code_content", "")
            if not isinstance(code_content, str):
                raise ValueError("Code content must be a string.")

            summary = metadata.get("summary")
            if not isinstance(summary, str):
                raise ValueError("Summary must be a string.")

            children_ids = metadata.get("children_ids", [])
            if not isinstance(children_ids, list) or not all(
                isinstance(child_id, str) for child_id in children_ids
            ):
                raise ValueError("Children IDs must be a list of strings.")

            important_comments_data = metadata.get("important_comments", [])
            if not isinstance(important_comments_data, list) or all(
                isinstance(comment, dict) for comment in important_comments_data
            ):
                raise ValueError("Important comments must be a list.")

            important_comments: list[CommentModel] = []
            for comment_data in important_comments_data:
                if not isinstance(comment_data, dict):
                    raise ValueError("Each important comment must be a dictionary.")
                comment: CommentModel = CommentModel._build_from_metadata(comment_data)
                important_comments.append(comment)

            dependencies: list[ImportModel | DependencyModel] = []
            dependencies_data = metadata.get("dependencies", [])
            if isinstance(dependencies_data, list):
                for dependency_data in dependencies_data:
                    if not isinstance(dependency_data, dict):
                        raise ValueError("Each dependency must be a dictionary.")
                    dependency = None
                    if "import_names" in dependency_data:
                        dependency = ImportModel._build_from_metadata(dependency_data)
                    elif "code_block_id" in dependency_data:
                        dependency = DependencyModel._build_from_metadata(
                            dependency_data
                        )
                    if not dependency:
                        raise ValueError("Invalid dependency.")
                    dependencies.append(dependency)
            else:
                raise ValueError("Dependencies must be a list.")

            return cls(
                id=id,
                file_path=file_path,
                parent_id=parent_id,
                block_type=BlockType[block_type],
                start_line_num=start_line_num,
                end_line_num=end_line_num,
                code_content=code_content,
                important_comments=important_comments,
                dependencies=dependencies,
                summary=summary if summary else None,
                children_ids=children_ids,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


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
        """Converts the module attributes to a metadata dictionary for ChromaDB."""

        return {
            "docstring": self._convert_docstring_to_metadata(),
            "header": self._convert_header_to_metadata(),
            "footer": self._convert_footer_to_metadata(),
            "imports": self._convert_imports_to_metadata(),
        }

    @classmethod
    def _build_from_meta(
        cls, metadata: dict[str, str | int | list[str]]
    ) -> "ModuleSpecificAttributes":
        """Builds a ModuleSpecificAttributes from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            docstring = metadata.get("docstring")
            if not isinstance(docstring, str):
                raise ValueError("Docstring must be a string.")

            header = metadata.get("header")
            if not isinstance(header, list):
                raise ValueError("Header must be a list.")

            footer = metadata.get("footer")
            if not isinstance(footer, list):
                raise ValueError("Footer must be a list.")

            imports_data = metadata.get("imports")
            if not isinstance(imports_data, list):
                raise ValueError("Imports must be a list.")

            imports = []
            for import_data in imports_data:
                if not isinstance(import_data, dict):
                    raise ValueError("Each import must be a dictionary.")
                import_model = ImportModel._build_from_metadata(import_data)
                imports.append(import_model)

            return cls(
                docstring=docstring,
                header=header,
                footer=footer,
                imports=imports,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class ModuleModel(BaseCodeBlockModel, ModuleSpecificAttributes):
    """
    Model for a module.

    Attributes:
        - id (str): The unique identifier for the module.
        - file_path (str): The path to the Python file that the module represents.
        - parent_id (str | None): The identifier of the parent (usually a directory).
        - block_type (BlockType): The type of code block that the module represents.
        - start_line_num (int): The line number of the first line of the module.
        - end_line_num (int): The line number of the last line of the module.
        - code_content (str): The string content of the module.
        - important_comments (list[CommentModel] | None): A list of important comments in the module.
        - dependencies (list[ImportModel | DependencyModel] | None): A list of dependencies for the module.
        - summary (str | None): A summary of the module.
        - children_ids (list[str] | None): A list of the identifiers of the children of the module.
        - docstring (str | None): The docstring of the module.
        - header (list[str] | None): The header of the module.
        - footer (list[str] | None): The footer of the module.
        - imports (list[ImportModel] | None): A list of import statements in the module.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the module model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata_dict: dict[str, str | int | list[str]]) -> ModuleModel`
            - Builds a ModuleModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the module model to a metadata dictionary for ChromaDB."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_module_attributes_to_metadata_dict(),
        }

    @classmethod
    def build_from_metadata(
        cls, metadata_dict: dict[str, str | int | list[str]]
    ) -> "ModuleModel":
        """
        Builds a ModuleModel from a metadata dictionary.

        Args:
            - metadata_dict (dict[str, str | int | list[str]]): A dictionary containing metadata for a module.

        Returns:
            ModuleModel: An instance of ModuleModel.

        Raises:
            - ValueError: If the metadata is not a dictionary.
            - ValueError: If the metadata is missing required keys.
            - ValueError: If the metadata contains invalid values.
            - Exception: If an unexpected error occurs.
        """
        try:
            if not isinstance(metadata_dict, dict):
                raise ValueError("Metadata must be a dictionary.")

            module_specific_attributes: ModuleSpecificAttributes = (
                ModuleSpecificAttributes._build_from_meta(metadata_dict)
            )
            base_code_block_model: BaseCodeBlockModel = (
                BaseCodeBlockModel._build_from_metadata(metadata_dict)
            )

            return cls(
                **module_specific_attributes.model_dump(),
                **base_code_block_model.model_dump(),
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


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

    @classmethod
    def _build_from_meta(
        cls, metadata: dict[str, str | int | list[str]]
    ) -> "ClassSpecificAttributes":
        """Builds a ClassSpecificAttributes from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            class_name = metadata.get("class_name")
            if not isinstance(class_name, str):
                raise ValueError("Class name must be a string.")

            decorators_data = metadata.get("decorators", [])
            if not isinstance(decorators_data, list):
                raise ValueError("Decorators must be a list.")

            decorators: list[DecoratorModel] = []
            for decorator_data in decorators_data:
                if not isinstance(decorator_data, dict):
                    raise ValueError("Each decorator must be a dictionary.")
                decorator: DecoratorModel = DecoratorModel._build_from_metadata(
                    decorator_data
                )
                decorators.append(decorator)

            bases = metadata.get("bases", [])
            if not isinstance(bases, list) or all(
                isinstance(base, str) for base in bases
            ):
                raise ValueError("Bases must be a list.")

            docstring = metadata.get("docstring")
            if not isinstance(docstring, str):
                raise ValueError("Docstring must be a string.")

            keywords_data = metadata.get("keywords", [])
            if not isinstance(keywords_data, list) or all(
                isinstance(keyword, dict) for keyword in keywords_data
            ):
                raise ValueError("Keywords must be a list.")

            keywords: list[ClassKeywordModel] = []
            for keyword_data in keywords_data:
                if not isinstance(keyword_data, dict):
                    raise ValueError("Each keyword must be a dictionary.")
                keyword: ClassKeywordModel = ClassKeywordModel._build_from_metadata(
                    keyword_data
                )
                keywords.append(keyword)

            return cls(
                class_name=class_name,
                decorators=decorators,
                bases=bases,
                docstring=docstring,
                keywords=keywords,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class ClassModel(BaseCodeBlockModel, ClassSpecificAttributes):
    """
    Model for a class.

    Attributes:
        - id (str): The unique identifier for the class.
        - file_path (str): The path to the Python file that the class represents.
        - parent_id (str | None): The identifier of the parent (usually a module).
        - block_type (BlockType): The type of code block that the class represents.
        - start_line_num (int): The line number of the first line of the class.
        - end_line_num (int): The line number of the last line of the class.
        - code_content (str): The string content of the class.
        - important_comments (list[CommentModel] | None): A list of important comments in the class.
        - dependencies (list[ImportModel | DependencyModel] | None): A list of dependencies for the class.
        - summary (str | None): A summary of the class.
        - children_ids (list[str] | None): A list of the identifiers of the children of the class.
        - class_name (str): The name of the class.
        - decorators (list[DecoratorModel] | None): A list of decorators for the class.
        - bases (list[str] | None): A list of base classes for the class.
        - docstring (str | None): The docstring of the class.
        - keywords (list[ClassKeywordModel] | None): A list of keywords for the class.


    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the class model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata_dict: dict[str, str | int | list[str]]) -> ClassModel`
            - Builds a ClassModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the class model to a metadata dictionary for ChromaDB."""
        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_class_attributes_to_metadata_dict(),
        }

    @classmethod
    def build_from_metadata(
        cls, metadata_dict: dict[str, str | int | list[str]]
    ) -> "ClassModel":
        """
        Builds a ClassModel from a metadata dictionary.

        Args:
            - metadata_dict (dict[str, str | int | list[str]]): A dictionary containing metadata for a class.

        Returns:
            ClassModel: An instance of ClassModel.

        Raises:
            - ValueError: If the metadata is not a dictionary.
            - ValueError: If the metadata is missing required keys.
            - ValueError: If the metadata contains invalid values.
            - Exception: If an unexpected error occurs.
        """
        try:
            if not isinstance(metadata_dict, dict):
                raise ValueError("Metadata must be a dictionary.")

            class_specific_attributes: ClassSpecificAttributes = (
                ClassSpecificAttributes._build_from_meta(metadata_dict)
            )
            base_code_block_model: BaseCodeBlockModel = (
                BaseCodeBlockModel._build_from_metadata(metadata_dict)
            )

            return cls(
                **class_specific_attributes.model_dump(),
                **base_code_block_model.model_dump(),
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


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
        """Converts the function attributes to a metadata dictionary for ChromaDB."""

        return {
            "function_name": self.function_name,
            "docstring": self._convert_docstring_to_metadata(),
            "decorators": self._convert_decorators_to_metadata(),
            "parameters": self._convert_parameters_to_metadata(),
            "returns": self._convert_returns_to_metadata(),
            "is_method": self.is_method,
            "is_async": self.is_async,
        }

    @classmethod
    def _build_from_meta(
        cls, metadata: dict[str, str | bool]
    ) -> "FunctionSpecificAttributes":
        """Builds a FunctionSpecificAttributes from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            function_name = metadata.get("function_name")
            if not isinstance(function_name, str):
                raise ValueError("Function name must be a string.")

            docstring = metadata.get("docstring")
            if not isinstance(docstring, str):
                raise ValueError("Docstring must be a string.")

            decorators_data = metadata.get("decorators", [])
            if not isinstance(decorators_data, list):
                raise ValueError("Decorators must be a list.")

            decorators: list[DecoratorModel] = []
            for decorator_data in decorators_data:
                if not isinstance(decorator_data, dict):
                    raise ValueError("Each decorator must be a dictionary.")
                decorator: DecoratorModel = DecoratorModel._build_from_metadata(
                    decorator_data
                )
                decorators.append(decorator)

            parameters_data = metadata.get("parameters")
            if not isinstance(parameters_data, dict):
                raise ValueError("Parameters must be a dictionary.")

            parameters: ParameterListModel = ParameterListModel._build_from_metadata(
                parameters_data
            )

            returns = metadata.get("returns")
            if not isinstance(returns, str):
                raise ValueError("Returns must be a string.")

            is_method = metadata.get("is_method")
            if not isinstance(is_method, bool):
                raise ValueError("is_method must be a boolean.")

            is_async = metadata.get("is_async")
            if not isinstance(is_async, bool):
                raise ValueError("is_async must be a boolean.")

            return cls(
                function_name=function_name,
                docstring=docstring,
                decorators=decorators,
                parameters=parameters,
                returns=returns,
                is_method=is_method,
                is_async=is_async,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class FunctionModel(BaseCodeBlockModel, FunctionSpecificAttributes):
    """
    A model for a function.

    Attributes:
        - id (str): The unique identifier for the function.
        - file_path (str): The path to the Python file that the function represents.
        - parent_id (str | None): The identifier of the parent (usually a module or class).
        - block_type (BlockType): The type of code block that the function represents.
        - start_line_num (int): The line number of the first line of the function.
        - end_line_num (int): The line number of the last line of the function.
        - code_content (str): The string content of the function.
        - important_comments (list[CommentModel] | None): A list of important comments in the function.
        - dependencies (list[ImportModel | DependencyModel] | None): A list of dependencies for the function.
        - summary (str | None): A summary of the function.
        - children_ids (list[str] | None): A list of the identifiers of the children of the function.
        - function_name (str): The name of the function.
        - docstring (str | None): The docstring of the function.
        - decorators (list[DecoratorModel] | None): A list of decorators for the function.
        - parameters (ParameterListModel | None): A model representing the function's parameters.
        - returns (str | None): A string representing the function's return annotation.
        - is_method (bool): True if the function is a method, False otherwise.
        - is_async (bool): True if the function is asynchronous, False otherwise.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the function model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata_dict: dict[str, str | int | list[str]]) -> FunctionModel`
            - Builds a FunctionModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the function model to a metadata dictionary for ChromaDB."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_function_attributes_to_metadata_dict(),
        }

    @classmethod
    def build_from_metadata(
        cls, metadata_dict: dict[str, str | int | list[str] | bool]
    ) -> "FunctionModel":
        """
        Builds a FunctionModel from a metadata dictionary.

        Args:
            - metadata_dict (dict[str, str | int | list[str]]): A dictionary containing metadata for a function.

        Returns:
            FunctionModel: An instance of FunctionModel.

        Raises:
            - ValueError: If the metadata is not a dictionary.
            - ValueError: If the metadata is missing required keys.
            - ValueError: If the metadata contains invalid values.
            - Exception: If an unexpected error occurs.
        """
        try:
            if not isinstance(metadata_dict, dict):
                raise ValueError("Metadata must be a dictionary.")

            function_specific_attributes: FunctionSpecificAttributes = (
                FunctionSpecificAttributes._build_from_meta(metadata_dict)  # type: ignore # FIXME: fix type hinting error
            )  # type: ignore # FIXME: fix type hinting error
            base_code_block_model: BaseCodeBlockModel = (
                BaseCodeBlockModel._build_from_metadata(metadata_dict)
            )

            return cls(
                **function_specific_attributes.model_dump(),
                **base_code_block_model.model_dump(),
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class StandaloneCodeBlockSpecificAttributes(BaseModel):
    """Standalone code block specific attributes."""

    variable_assignments: list[str] | None = None

    def _convert_variable_assignments_to_metadata(self) -> str:
        """Converts the variable assignments to a metadata string."""
        return self.model_dump_json() if self.variable_assignments else ""

    def _convert_standalone_block_attributes_to_metadata_dict(
        self,
    ) -> dict[str, str | int]:
        """Converts the standalone code block attributes to a metadata dictionary for ChromaDB."""
        return {
            "variable_assignments": self._convert_variable_assignments_to_metadata(),
        }

    @classmethod
    def _build_from_meta(
        cls, metadata: dict[str, str | int | list[str]]
    ) -> "StandaloneCodeBlockSpecificAttributes":
        """Builds a StandaloneCodeBlockSpecificAttributes from a metadata dictionary."""

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            variable_assignments_data = metadata.get("variable_assignments", [])
            if not isinstance(variable_assignments_data, list):
                raise ValueError("Variable assignments must be a list.")

            variable_assignments: list[str] = []
            for variable_assignment_data in variable_assignments_data:
                if not isinstance(variable_assignment_data, str):
                    raise ValueError("Each variable assignment must be a string.")
                variable_assignments.append(variable_assignment_data)

            return cls(
                variable_assignments=variable_assignments,
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class StandaloneCodeBlockModel(
    BaseCodeBlockModel, StandaloneCodeBlockSpecificAttributes
):
    """
    Model for a standalone code block.

    Attributes:
        - id (str): The unique identifier for the standalone code block.
        - file_path (str): The path to the Python file that the standalone code block represents.
        - parent_id (str | None): The identifier of the parent (usually a module or class).
        - block_type (BlockType): The type of code block that the standalone code block represents.
        - start_line_num (int): The line number of the first line of the standalone code block.
        - end_line_num (int): The line number of the last line of the standalone code block.
        - code_content (str): The string content of the standalone code block.
        - important_comments (list[CommentModel] | None): A list of important comments in the standalone code block.
        - dependencies (list[ImportModel | DependencyModel] | None): A list of dependencies for the standalone code block.
        - summary (str | None): A summary of the standalone code block.
        - children_ids (list[str] | None): A list of the identifiers of the children of the standalone code block.
        - variable_assignments (list[str] | None): A list of variable assignments in the standalone code block.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`
            - Converts the standalone code block model to a metadata dictionary for ChromaDB.
        - `build_from_metadata(metadata_dict: dict[str, str | int | list[str]]) -> StandaloneCodeBlockModel`
            - Builds a StandaloneCodeBlockModel from a metadata dictionary.
    """

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the standalone code block model to a metadata dictionary for ChromaDB."""

        return {
            **self._convert_base_attributes_to_metadata_dict(),
            **self._convert_standalone_block_attributes_to_metadata_dict(),
        }

    @classmethod
    def _build_from_meta(
        cls, metadata: dict[str, str | int | list[str]]
    ) -> "StandaloneCodeBlockModel":
        """
        Builds a StandaloneCodeBlockModel from a metadata dictionary.

        Args:
            - metadata_dict (dict[str, str | int | list[str]]): A dictionary containing metadata for a standalone code block.

        Returns:
            - StandaloneCodeBlockModel: An instance of StandaloneCodeBlockModel.

        Raises:
            - ValueError: If the metadata is not a dictionary.
            - ValueError: If the metadata is missing required keys.
            - ValueError: If the metadata contains invalid values.
            - Exception: If an unexpected error occurs.
        """

        try:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

            standalone_code_block_specific_attributes: (
                StandaloneCodeBlockSpecificAttributes
            ) = StandaloneCodeBlockSpecificAttributes._build_from_meta(metadata)
            base_code_block_model: BaseCodeBlockModel = (
                BaseCodeBlockModel._build_from_metadata(metadata)
            )

            return cls(
                **standalone_code_block_specific_attributes.model_dump(),
                **base_code_block_model.model_dump(),
            )
        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e


class DirectoryModel(BaseModel):
    """
    Model for a directory.

    Attributes:
        - id (str): The unique identifier for the directory.
        - block_type (BlockType): The type of code block that the directory represents.
        - directory_name (str): The name of the directory.
        - sub_directories_ids (list[str]): A list of the identifiers of the sub-directories of the directory.
        - children_ids (list[str]): A list of the identifiers of the children of the directory.
        - parent_id (str | None): The identifier of the parent (usually a directory).
        - summary (str | None): A summary of the directory.

    Methods:
        - `convert_to_metadata() -> dict[str, str | int]`:
            Converts the directory model to a metadata dictionary for ChromaDB.
    """

    id: str
    block_type: BlockType = BlockType.DIRECTORY
    directory_name: str
    sub_directories_ids: list[str]
    children_ids: list[str]
    parent_id: str | None
    summary: str | None = None

    def convert_to_metadata(self) -> dict[str, str | int]:
        """Converts the directory model to a metadata dictionary for ChromaDB."""

        return {
            "directory_name": self.directory_name,
            "sub_directories": (
                str(self.sub_directories_ids) if self.sub_directories_ids else ""
            ),
            "children_ids": self.model_dump_json() if self.children_ids else "",
            "parent_id": self.parent_id if self.parent_id else "",
            "summary": self.summary if self.summary else "",
        }

    @classmethod
    def build_from_metadata(
        cls, metadata_dict: dict[str, str | list[str]]
    ) -> "DirectoryModel":
        """
        Builds a DirectoryModel from a metadata dictionary.

        Args:
            - metadata_dict (dict[str, str | int | list[str]]): A dictionary containing metadata for a directory.

        Returns:
            - DirectoryModel: An instance of DirectoryModel.

        Raises:
            - ValueError: If the metadata is not a dictionary.
            - ValueError: If the metadata is missing required keys.
            - ValueError: If the metadata contains invalid values.
            - Exception: If an unexpected error occurs.
        """

        try:
            if not isinstance(metadata_dict, dict):
                raise ValueError("Metadata must be a dictionary.")

            id = metadata_dict.get("id")
            if not isinstance(id, str):
                raise ValueError("ID must be a string.")

            directory_name = metadata_dict.get("directory_name")
            if not isinstance(directory_name, str):
                raise ValueError("Directory name must be a string.")

            sub_directories_ids = metadata_dict.get("sub_directories")
            if not isinstance(sub_directories_ids, list) or not all(
                isinstance(sub_directory_id, str)
                for sub_directory_id in sub_directories_ids
            ):
                raise ValueError("Sub-directories must be a list of strings.")

            children_ids = metadata_dict.get("children_ids")
            if not isinstance(children_ids, list) or not all(
                isinstance(child_id, str) for child_id in children_ids
            ):
                raise ValueError("Children IDs must be a list of strings.")

            parent_id = metadata_dict.get("parent_id")
            if not isinstance(parent_id, str):
                raise ValueError("Parent ID must be a string.")

            summary = metadata_dict.get("summary")
            if not isinstance(summary, str):
                raise ValueError("Summary must be a string.")

            return cls(
                id=id,
                directory_name=directory_name,
                sub_directories_ids=sub_directories_ids,
                children_ids=children_ids,
                parent_id=parent_id if parent_id else None,
                summary=summary if summary else None,
            )

        except ValueError as ve:
            logging.error(f"Error building from metadata: {ve}")
            raise ve
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise e
