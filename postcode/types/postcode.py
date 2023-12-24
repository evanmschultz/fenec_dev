from typing import Union
from postcode.models.models import (
    ClassModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
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
]

BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]
