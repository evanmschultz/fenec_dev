from abc import ABC
from typing import Literal, Protocol
from dataclasses import dataclass

from pydantic import BaseModel

from postcode.ai_services.summarizer.prompts import summarization_prompts
from postcode.ai_services.chat.prompts import chat_prompts


class SummarizationConfigs(ABC):
    """
    SummarizerConfigs is an abstract base class for summarizer configurations.
    """

    ...


class ChatConfigs(ABC):
    """
    ChatConfigs is an abstract base class for chat configurations.
    """

    ...


class OpenAIConfigs(BaseModel):
    """
    Configs for the summarization completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - `system_message` (str): The system message used for chat completion.
        - `model` (str): The model to use for the completion. Default is "gpt-4o".
        - `max_tokens` (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - `stream` (bool): Whether to stream back partial progress. Default is False.
        - `temperature` (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - model must be a valid OpenAI model name.

    Examples:
        ```Python
        system_message = "Summarize the following code."
        summary_completion_configs = SummaryCompletionConfigs(
            system_message=system_message,
            model="gpt-4o",
            max_tokens=100,
            presence_penalty=0.0,
            stream=False,
            temperature=0.0,
        )
        ```
    """

    system_message: str = summarization_prompts.SUMMARIZER_DEFAULT_INSTRUCTIONS
    model: Literal[
        "gpt-4o",
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
    ] = "gpt-4o"
    max_tokens: int | None = None
    stream: bool = False
    temperature: float = 0.0


class OpenAISummarizationConfigs(SummarizationConfigs, OpenAIConfigs):
    """
    Configs for the summarization completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - `system_message` (str): The system message used for chat completion.
        - `model` (str): The model to use for the completion. Default is "gpt-4o".
        - `max_tokens` (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - `stream` (bool): Whether to stream back partial progress. Default is False.
        - `temperature` (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - model must be a valid OpenAI model name.

    Examples:
        ```Python
        system_message = "Summarize the following code."
        summary_completion_configs = SummaryCompletionConfigs(
            system_message=system_message,
            model="gpt-4o",
            max_tokens=100,
            presence_penalty=0.0,
            stream=False,
            temperature=0.0,
        )
        ```
    """


class OpenAIChatConfigs(OpenAISummarizationConfigs, ChatConfigs):
    """
    Configs for the chat completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - `system_message` (str): The system message used for chat completion.
        - `model` (str): The model to use for the completion. Default is "gpt-4o".
        - `max_tokens` (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - `stream` (bool): Whether to stream back partial progress. Default is False.
        - `temperature` (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - model must be a valid OpenAI model name.

    Examples:
        ```Python
        system_message = "Summarize the following code."
        chat_completion_configs = ChatCompletionConfigs(
            system_message=system_message,
            model="gpt-4o",
            max_tokens=100,
            presence_penalty=0.0,
            stream=False,
            temperature=0.0,
        )
        ```
    """

    system_message: str = chat_prompts.DEFAULT_SYSTEM_PROMPT


class OllamaSummarizationConfigs(SummarizationConfigs, BaseModel):
    """
    Configs for the Ollama completion.

    Used to set the chat completion parameters for the Ollama chat completions method call.

    Args:
        - `model` (str): The model to use for the completion. Default is "gpt-4o".
        - `max_tokens` (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - `stream` (bool): Whether to stream back partial progress. Default is False.
        - `temperature` (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - `model` must be a valid Ollama model name with a valid parameter syntax.

    Examples:
        ```Python
        ollama_completion_configs = OllamaConfigs(
            model="codellama:13b-python",
        ```
    """

    model: str = "codellama:7b"
    system_message: str = summarization_prompts.SUMMARIZER_DEFAULT_INSTRUCTIONS


class OllamaChatConfigs(ChatConfigs, BaseModel):
    """
    Configs for the Ollama completion.

    Used to set the chat completion parameters for the Ollama chat completions method call.

    Args:
        - `model` (str): The model to use for the completion. Default is "gpt-4o".
        - `max_tokens` (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - `stream` (bool): Whether to stream back partial progress. Default is False.
        - `temperature` (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - `model` must be a valid Ollama model name with a valid parameter syntax.

    Examples:
        ```Python
        ollama_completion_configs = OllamaConfigs(
            model="codellama:13b",
        ```
    """

    model: str = "codellama:7b"
    system_message: str = chat_prompts.DEFAULT_SYSTEM_PROMPT


@dataclass
class OpenAIReturnContext:
    """
    A dataclass for storing the return context of an OpenAI completion.

    Attributes:
        - `prompt_tokens` (int): The number of tokens in the prompt.
        - `completion_tokens` (int): The number of tokens in the completion.
        - `summary` (str | None): The summary of the code snippet.
    """

    prompt_tokens: int
    completion_tokens: int
    summary: str | None
