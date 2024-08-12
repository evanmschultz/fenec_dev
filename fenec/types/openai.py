"""
OpenAI Types
------------

This module contains types defined by the openai third-party library.
These types are used for easy implementation in the fenec project and
provide convenience for users of the fenec library.
"""

from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
