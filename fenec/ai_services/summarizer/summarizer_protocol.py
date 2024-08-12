from typing import Protocol
from fenec.utilities.configs.configs import OpenAIReturnContext


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
        parent_summary: str | None = None,
        pass_number: int = 1,
        previous_summary: str | None = None,
    ) -> OpenAIReturnContext | str | None:
        """
        Summarizes the provided code snippet.

        Args:
            - `code` (str): The code snippet to summarize.
            - `model_id` (str): The identifier of the model_id being summarized.
            - `children_summaries` (str | None): Summaries of child elements, if any.
            - `dependency_summaries` (str | None): Summaries of dependencies, if any.
            - `import_details` (str | None): Details of imports used in the code.
            - `parent_summary` (str | None): Summary of the parent element, if applicable.
            - `pass_number` (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            OpenAIReturnContext | str | None: The summary context, or None if summarization fails.
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
        parent_summary: str | None = None,
        pass_number: int = 1,
    ) -> OpenAIReturnContext | None:
        """
        A method for testing the summarize_code functionality without making API calls.

        Args:
            - code (str): The code snippet to summarize (not used in the test method).
            - model_id (str): The identifier of the model_id being summarized.
            - children_summaries (str | None): Summaries of child elements, if any.
            - dependency_summaries (str | None): Summaries of dependencies, if any.
            - import_details (str | None): Details of imports used in the code.
            - parent_summary (str | None): Summary of the parent element, if applicable.
            - pass_number (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            `OpenAIReturnContext | None`: A context object containing a test summary and token usage information.
        """
        ...
