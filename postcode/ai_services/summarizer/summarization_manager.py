import logging
from typing import Union

from postcode.ai_services.summarizer.summarization_context import (
    Summarizer,
    OpenAIReturnContext,
)

# from postcode.types.postcode import ModelType

from postcode.models.models import (
    ClassModel,
    DependencyModel,
    FunctionModel,
    ImportModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]


class SummarizationManager:
    ...
