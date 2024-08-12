from typing import Any

from fenec.python_parser.model_builders.base_model_builder import BaseModelBuilder

from fenec.utilities.logger.decorators import logging_decorator
from fenec.models.models import (
    DecoratorModel,
    FunctionModel,
    FunctionSpecificAttributes,
    ParameterListModel,
)
from fenec.models.enums import BlockType


class FunctionModelBuilder(BaseModelBuilder):
    """
    A builder class for constructing a model of a Python function.

    This class extends BaseModelBuilder and specializes in building a detailed model of a Python function, capturing various aspects such as function name, docstring, parameters, decorators, return type, and whether the function is a method or asynchronous.

    Attributes:
        - function_attributes (FunctionSpecificAttributes): An instance containing attributes specific to a function.

    Args:
        - id (str): The unique identifier for the function model.
        - function_name (str): The name of the function.
        - parent_id (str): The identifier of the parent model (e.g., module or class containing this function).
    """

    def __init__(
        self, id: str, function_name: str, parent_id: str, file_path: str
    ) -> None:
        super().__init__(
            id=id,
            file_path=file_path,
            block_type=BlockType.FUNCTION,
            parent_id=parent_id,
        )
        self.function_attributes = FunctionSpecificAttributes(
            function_name=function_name,
            docstring=None,
            decorators=None,
            parameters=None,
            is_method=False,
            is_async=False,
            returns=None,
        )

    def set_parameters_list(
        self, parameter_list_model: ParameterListModel | None
    ) -> "FunctionModelBuilder":
        """Adds a parameter to the function model."""
        self.function_attributes.parameters = parameter_list_model
        return self

    def set_decorators(
        self, decorators: list[DecoratorModel] | None
    ) -> "FunctionModelBuilder":
        """Adds decorator to the decorators list in the class model."""
        if decorators:
            self.function_attributes.decorators = decorators
        else:
            self.function_attributes.decorators = None
        return self

    def set_docstring(self, docstring: str | None) -> "FunctionModelBuilder":
        """Sets the docstring."""
        self.function_attributes.docstring = docstring
        return self

    def set_return_annotation(self, return_type: str) -> "FunctionModelBuilder":
        """Sets the return type."""
        self.function_attributes.returns = return_type
        return self

    def set_is_method(self, is_method: bool) -> "FunctionModelBuilder":
        """Sets the is_method attribute in the function model."""
        self.function_attributes.is_method = is_method
        return self

    def set_is_async(self, is_async: bool) -> "FunctionModelBuilder":
        """Sets the is_async attribute in the function model."""
        self.function_attributes.is_async = is_async
        return self

    def _get_function_specific_attributes(self) -> dict[str, Any]:
        """
        Gets the function specific attributes from the builder.
        """
        return self.function_attributes.model_dump()

    @logging_decorator(message="Building function model")
    def build(self) -> FunctionModel:
        """Builds and returns the function model instance after building and setting the children models."""
        self.build_children()
        self.set_children_ids()
        return FunctionModel(
            **self._get_common_attributes(),
            **self._get_function_specific_attributes(),
        )
