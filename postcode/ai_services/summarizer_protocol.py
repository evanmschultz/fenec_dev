from typing import Protocol

import postcode.ai_services.summarizer_configs as configs
import postcode.ai_services.summarizer_context as context


class Summarizer(Protocol):
    def summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: configs.SummaryCompletionConfigs = configs.SummaryCompletionConfigs(),
    ) -> context.OpenAIReturnContext | str:
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

    def test_summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: configs.SummaryCompletionConfigs = configs.SummaryCompletionConfigs(),
    ) -> context.OpenAIReturnContext | str:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            code (str): The code snippet to summarize (pass in dummy string).
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
