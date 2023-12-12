from typing import Literal, Protocol

from pydantic import BaseModel

from openai import OpenAI
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from ai_services.temp import code_example
from ai_services.prompts.summarization_prompts import (
    SUMMARIZER_DEFAULT_INSTRUCTIONS,
    COD_SUMMARIZATION_PROMPT,
    summary_prompt_list,
)


class SummaryCompletionConfigs(BaseModel):
    """
    Configs for the summarization completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - system_message (str): The system message used for chat completion.
        - prompt_template (str): The prompt template used for chat completion. This should contain "{code}" to
            insert the code at that point; otherwise, the code snippet will be appended below the prompt.
        - model (str): The model to use for the completion. Default is "gpt-4-1106-preview".
        - max_tokens (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - presence_penalty (float | None): Penalty for new tokens based on their presence in the text so far.
            Default is None.
        - stream (bool): Whether to stream back partial progress. Default is False.
        - temperature (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - prompt_template should contain "{code}", if not, the code snippet will be appended below the prompt.
        - model must be a valid OpenAI model name.

    Examples:
        >>> system_message = "Summarize the following code."
        >>> prompt_template = '''Summarize the following code.
        ... CODE:
        ... ```Python
        ... {code}
        ... ```
        ... '''
        >>> summary_completion_configs = SummaryCompletionConfigs(
        ...     system_message=system_message,
        ...     prompt_template=prompt_template,
        ...     model="gpt-4-1106-preview",
        ...     max_tokens=100,
        ...     presence_penalty=0.0,
        ...     stream=False,
        ...     temperature=0.0,
        ... )
    """

    system_message: str = SUMMARIZER_DEFAULT_INSTRUCTIONS
    prompt_template: str = COD_SUMMARIZATION_PROMPT
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


class Summarizer(Protocol):
    def summarize_code(
        self,
        code: str,
        *,
        configs: SummaryCompletionConfigs = SummaryCompletionConfigs(),
    ) -> str:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            code (str): The code snippet to summarize.
            configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            >>> client = OpenAI()
            >>> summarizer = Summarizer(client=client)
            >>> code_example = "print('Hello, world')"
            >>> summary = summarizer.summarize_code(code_example)
            >>> print(summary)
        """
        ...


class OpenAISummarizer:
    """
    A class for summarizing code snippets using the OpenAI API.

    Args:
        - client (OpenAI): The OpenAI client used for making API requests.
        - summary_prompt_list (list[str], optional): A list of summary prompts to be used. Defaults to an empty list.

    Attributes:
        - client (OpenAI): The OpenAI client used for making API requests.
        - prompt_list (list[str]): A list of summary prompts.
        - default_prompt (str): The default summary prompt.

    Methods:
        summarize_code(code: str, configs: SummaryCompletionConfigs = SummaryCompletionConfigs()) -> str:
            Summarizes the provided code snippet using the OpenAI API.

    Examples:
        >>> client = OpenAI()
        >>> summarizer = Summarizer(client=client)
        >>> code_example = "print('Hello, world')"
        >>> summary = summarizer.summarize_code(code_example)
        >>> print(summary)
    """

    def __init__(
        self, client: OpenAI, *, summary_prompt_list: list[str] = summary_prompt_list
    ) -> None:
        self.client: OpenAI = client
        self.prompt_list: list[str] = summary_prompt_list
        self.default_prompt: str = self.prompt_list[0]

    def _create_system_message(self, content: str) -> ChatCompletionSystemMessageParam:
        """Creates a system message for chat completion using OpenAi's ChatCompletionSystemMessageParam class."""
        return ChatCompletionSystemMessageParam(content=content, role="system")

    def _create_user_message(self, content: str) -> ChatCompletionUserMessageParam:
        """Creates a user message for chat completion using OpenAi's ChatCompletionUserMessageParam class."""
        return ChatCompletionUserMessageParam(content=content, role="user")

    def _create_messages_list(
        self,
        system_message: str,
        user_message: str,
    ) -> list[ChatCompletionMessageParam]:
        """
        Creates a list of messages for chat completion, including both system and user messages.

        Args:
            system_message (str): The system message content.
            user_message (str): The user message content.

        Returns:
            list[ChatCompletionMessageParam]: A list containing the system and user messages as OpenAI's
                ChatCompletionMessageParam classes.
        """

        return [
            self._create_system_message(system_message),
            self._create_user_message(user_message),
        ]

    def _interpolate_prompt(self, code: str, prompt_template: str | None = None) -> str:
        """
        Returns the prompt_template for the code snippet.

        Args:
            code (str): The code snippet.
            prompt_template (str | None): Custom prompt to be used. Defaults to None.

        Returns:
            str: The formatted prompt.

        Notes:
            - If prompt_template is not provided, the default prompt will be used.
            - If prompt_template contains "{code}", it will be replaced with the code snippet.
            - If prompt_template does not contain "{code}", the code snippet will be appended below the prompt_template.
        """

        if not prompt_template:
            return self.default_prompt.format(code=code)

        else:
            if "{code}" in prompt_template:
                return prompt_template.format(code=code)
            else:
                return f"{prompt_template}\n\n{code}"

    def _get_summary(
        self,
        messages: list[ChatCompletionMessageParam],
        *,
        configs: SummaryCompletionConfigs,
    ) -> str | None:
        """
        Retrieves the summary from the OpenAI API based on the provided messages and configuration settings.

        Args:
            messages (list[ChatCompletionMessageParam]): A list of messages for chat completion.
            configs (SummaryCompletionConfigs): Configuration settings for the summarization completion.

        Returns:
            str | None: The summary generated by the OpenAI API, or None if no summary is found.
        """

        response = self.client.chat.completions.create(
            messages=messages,
            model=configs.model,
            max_tokens=configs.max_tokens,
            stream=configs.stream,
            temperature=configs.temperature,
        )
        return response.choices[0].message.content  # type: ignore # FIXME: Fix type error

    def summarize_code(
        self,
        code: str,
        *,
        configs: SummaryCompletionConfigs = SummaryCompletionConfigs(),
    ) -> str:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            code (str): The code snippet to summarize.
            configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            >>> client = OpenAI()
            >>> summarizer = Summarizer(client=client)
            >>> code_example = "print('Hello, world')"
            >>> summary = summarizer.summarize_code(code_example)
            >>> print(summary)
        """

        prompt: str = self._interpolate_prompt(code, configs.prompt_template)
        messages: list[ChatCompletionMessageParam] = self._create_messages_list(
            system_message=configs.system_message, user_message=prompt
        )

        summary: str | None = self._get_summary(messages, configs=configs)
        return summary if summary else "Summary not found."


if __name__ == "__main__":
    client = OpenAI()
    summarizer = OpenAISummarizer(client=client)
    summary = summarizer.summarize_code(code_example)
    print(summary)
