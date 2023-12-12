from typing import Any

from model_builders.base_model_builder import BaseModelBuilder

from utilities.logger.decorators import logging_decorator
from models.models import (
    ModuleModel,
    ImportModel,
    ModuleSpecificAttributes,
)
from models.enums import BlockType


class ModuleModelBuilder(BaseModelBuilder):
    """
    A builder class for constructing a model of a Python module.

    This class extends BaseModelBuilder and specializes in building a detailed model of a Python module, capturing various aspects such as the module's docstring, header content, footer content, and imports. It allows for the incremental construction of the module model by adding or setting various components.

    Attributes:
        module_attributes (ModuleSpecificAttributes): An instance containing attributes specific to a module, like file path, docstring, header, footer, and imports.

    Args:
        id (str): The unique identifier for the module model.
        file_path (str): The file path of the module being modeled.

    Example:
        >>> module_builder = ModuleModelBuilder(id='module1', file_path='/path/to/module.py')
        >>> module_builder.set_docstring("This is a docstring").add_import(some_import_model)
        # Configures the module builder with a docstring and an import.
    """

    def __init__(self, id: str, file_path: str) -> None:
        super().__init__(id=id, block_type=BlockType.MODULE, parent_id=None)

        self.module_attributes = ModuleSpecificAttributes(
            file_path=file_path,
            docstring=None,
            header=None,
            footer=None,
            imports=None,
        )

    def set_docstring(self, docstring: str | None) -> "ModuleModelBuilder":
        """Set the docstring."""
        if docstring:
            self.module_attributes.docstring = docstring
        return self

    def set_header_content(self, header_content: list[str]) -> "ModuleModelBuilder":
        """Set the header."""
        if not self.module_attributes.header:
            self.module_attributes.header = []
        for line in header_content:
            self.module_attributes.header.append(line)
        return self

    def set_footer_content(self, footer_content: list[str]) -> "ModuleModelBuilder":
        """Set the footer."""
        if not self.module_attributes.footer:
            self.module_attributes.footer = []
        for line in footer_content:
            self.module_attributes.footer.append(line)
        return self

    def add_import(self, import_model: ImportModel) -> "ModuleModelBuilder":
        """Add an import to the imports list."""
        if not self.module_attributes.imports:
            self.module_attributes.imports = []
        # if "OpenAISummarizer" in [name.name for name in import_model.import_names]:
        #     print("Adding OpenAISummarizer import")
        self.module_attributes.imports.append(import_model)
        return self

    def update_import(
        self, updated_import_model: ImportModel, old_import_model: ImportModel
    ) -> "ModuleModelBuilder":
        """
        Update an import in the imports list.

        Loops through the imports list and replaces the old import with the updated import.

        Args:
            updated_import_model (ImportModel): The updated import model.
            old_import_model

        Returns:
            ModuleModelBuilder: The module model builder instance.

        Raises:
            Exception: If the import to be updated is not found.
        """
        if self.module_attributes.imports:
            import_to_remove: ImportModel | None = None
            for existing_import in self.module_attributes.imports:
                if (
                    existing_import.import_names == old_import_model.import_names
                    and existing_import.imported_from == old_import_model.imported_from
                    and existing_import.import_module_type
                    == old_import_model.import_module_type
                ):
                    import_to_remove = existing_import
                    # if "OpenAISummarizer" in [
                    #     name.name for name in existing_import.import_names
                    # ]:
                    #     print("Updating OpenAISummarizer import")
                    break

            if not import_to_remove:
                # raise Exception(f"Could not find import to remove: {old_import_model}")
                # print(f"Could not find import to remove: {old_import_model}")
                ...
            else:
                self.module_attributes.imports.remove(import_to_remove)
                self.module_attributes.imports.append(updated_import_model)
        else:
            raise Exception(
                f"No imports in the builders imports list: {self.module_attributes.imports}"
            )
        return self

    def _get_module_specific_attributes(self) -> dict[str, Any]:
        """Get the module specific attributes."""
        return self.module_attributes.model_dump()

    @logging_decorator(message="Building module model")
    def build(self) -> ModuleModel:
        """Builds and returns the module model instance after building and setting the children models."""
        self.build_and_set_children()
        return ModuleModel(
            **self._get_common_attributes(), **self._get_module_specific_attributes()
        )
