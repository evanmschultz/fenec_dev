from typing import Literal, Protocol
from dataclasses import dataclass

from pydantic import BaseModel

from postcode.ai_services.summarizer.prompts import summarization_prompts


class SummaryCompletionConfigs(BaseModel):
    """
    Configs for the summarization completion.

    Used to set the chat completion parameters for the OpenAI chat completions method call.

    Args:
        - system_message (str): The system message used for chat completion.
        - model (str): The model to use for the completion. Default is "gpt-4-1106-preview".
        - max_tokens (int | None): The maximum number of tokens to generate. 'None' implies no limit. Default is None.
        - stream (bool): Whether to stream back partial progress. Default is False.
        - temperature (float): Sampling temperature to use. Default is 0.0.

    Notes:
        - model must be a valid OpenAI model name.

    Examples:
        ```Python
        system_message = "Summarize the following code."
        summary_completion_configs = SummaryCompletionConfigs(
            system_message=system_message,
            model="gpt-4-1106-preview",
            max_tokens=100,
            presence_penalty=0.0,
            stream=False,
            temperature=0.0,
        )
        ```
    """

    system_message: str = summarization_prompts.SUMMARIZER_DEFAULT_INSTRUCTIONS
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


@dataclass
class OpenAIReturnContext:
    """
    A dataclass for storing the return context of an OpenAI completion.

    Attributes:
        - prompt_tokens (int): The number of tokens in the prompt.
        - completion_tokens (int): The number of tokens in the completion.
        - summary (str | None): The summary of the code snippet.
    """

    prompt_tokens: int
    completion_tokens: int
    summary: str | None


class Summarizer(Protocol):
    def summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: SummaryCompletionConfigs = SummaryCompletionConfigs(),
    ) -> OpenAIReturnContext | None:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            - code (str): The code snippet to summarize.
            - configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            ```Python
            client = OpenAI()

            # Create a summarizer instance with the OpenAI client
            summarizer = Summarizer(client=client)
            code_example = "print('Hello, world')"

            # Summarize the code snippet
            summary = summarizer.summarize_code(code_example)
            print(summary)
            ```
        """
        ...

    def test_summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: SummaryCompletionConfigs = SummaryCompletionConfigs(),
    ) -> OpenAIReturnContext | None:
        """
        A method for testing whether or not a summary path is working as expected.

        Args:
            - code (str): The code snippet to summarize (pass in dummy string).
            - configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            ```Python
            client = OpenAI()
            summarizer = Summarizer(client=client)
            code_example = "print('Hello, world')"

            # Run summary tester the code snippet
            summary = summarizer.summarize_code(code_example)
            print(summary)
            ```
        """
        ...
