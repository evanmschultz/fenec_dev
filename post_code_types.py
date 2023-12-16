from typing import Union

from python_parser.model_builders.class_model_builder import ClassModelBuilder
from python_parser.model_builders.function_model_builder import FunctionModelBuilder
from python_parser.model_builders.module_model_builder import ModuleModelBuilder
from python_parser.model_builders.standalone_block_model_builder import (
    StandaloneBlockModelBuilder,
)

BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]
