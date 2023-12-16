from typing import Literal

from pydantic import BaseModel
from ai_services.prompts.summarization_prompts import (
    SUMMARIZER_DEFAULT_INSTRUCTIONS,
)


class SummaryCompletionConfigs(BaseModel):
    """
    Configs for the summarization completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - system_message (str): The system message used for chat completion.
        - model (str): The model to use for the completion. Default is "gpt-4-1106-preview".
        - max_tokens (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - presence_penalty (float | None): Penalty for new tokens based on their presence in the text so far.
            Default is None.
        - stream (bool): Whether to stream back partial progress. Default is False.
        - temperature (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - model must be a valid OpenAI model name.

    Examples:
        >>> system_message = "Summarize the following code."
        >>> summary_completion_configs = SummaryCompletionConfigs(
        ...     system_message=system_message,
        ...     model="gpt-4-1106-preview",
        ...     max_tokens=100,
        ...     presence_penalty=0.0,
        ...     stream=False,
        ...     temperature=0.0,
        ... )
    """

    system_message: str = SUMMARIZER_DEFAULT_INSTRUCTIONS
    model: Literal[
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
    ] = "gpt-4-1106-preview"
    max_tokens: int | None = None
    stream: bool = False
    temperature: float = 0.0
