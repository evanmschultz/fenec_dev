"""
PostCode types
--------------

This module contains types defined by the postcode library.
These types are used for easy implementation in the postcode project and
provide convenience for users of the postcode library.
"""

from typing import Union
from postcode.models.models import (
    ClassModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
)

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

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
]

BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]
