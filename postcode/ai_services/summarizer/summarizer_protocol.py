from typing import Protocol
from postcode.ai_services.openai_configs import OpenAIReturnContext


class Summarizer(Protocol):
    """A protocol for summary classes."""

    def summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
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
        pass

    def test_summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
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
        pass
