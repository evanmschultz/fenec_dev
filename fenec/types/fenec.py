"""
Fenec types
--------------

This module contains types defined by the fenec library.
These types are used for easy implementation in the fenec project and
provide convenience for users of the fenec library.
"""

from typing import Union
from fenec.models.models import (
    ClassModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
)

from fenec.python_parser.model_builders.class_model_builder import ClassModelBuilder
from fenec.python_parser.model_builders.function_model_builder import (
    FunctionModelBuilder,
)
from fenec.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)
from fenec.python_parser.model_builders.standalone_block_model_builder import (
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
