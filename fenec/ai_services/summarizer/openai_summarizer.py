import logging

from openai import OpenAI
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion

from fenec.ai_services.summarizer.prompts.prompt_creator import (
    SummarizationPromptCreator,
)
from fenec.configs import (
    OpenAISummarizationConfigs,
    OpenAIReturnContext,
)


class OpenAISummarizer:
    """
    A class for summarizing code snippets using the OpenAI API.

    This class provides functionality to generate summaries of code snippets using OpenAI's language models.
    It supports multi-pass summarization, allowing for more comprehensive and context-aware summaries.

    Args:
        - `configs` (OpenAISummarizationConfigs, optional): Configuration settings for the OpenAI summarizer.

    Attributes:
        - client (OpenAI): The OpenAI client instance.
        - configs (OpenAISummarizationConfigs): Configuration settings for the summarizer.

    Methods:
        - summarize_code: Summarizes the provided code snippet using the OpenAI API.
        - test_summarize_code: A method for testing the summarization functionality.

    Example:
        ```Python
        summarizer = OpenAISummarizer()
        summary = summarizer.summarize_code(
            code="def hello_world():\n    print('Hello, world!')",
            model_id="function_1",
            children_summaries="No child functions.",
            dependency_summaries="No dependencies.",
            import_details="No imports.",
            parent_summary="Module containing greeting functions.",
            pass_number=1
        )
        print(summary.summary if summary else "Summarization failed")
        ```
    """

    def __init__(
        self,
        configs: OpenAISummarizationConfigs = OpenAISummarizationConfigs(),
    ) -> None:
        self.client: OpenAI = OpenAI()
        self.configs: OpenAISummarizationConfigs = configs

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
            - system_message (str): The system message content.
            - user_message (str): The user message content.

        Returns:
            - list[ChatCompletionMessageParam]: A list containing the system and user messages as OpenAI's
                ChatCompletionMessageParam classes.
        """

        return [
            self._create_system_message(system_message),
            self._create_user_message(user_message),
        ]

    def _create_prompt(
        self,
        code: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        parent_summary: str | None,
        pass_number: int,
        previous_summary: str | None,
    ) -> str:
        """
        Creates a prompt for code summarization.

        Args:
            - code (str): The code to summarize.
            - children_summaries (str | None): Summaries of child elements.
            - dependency_summaries (str | None): Summaries of dependencies.
            - import_details (str | None): Details of imports.
            - parent_summary (str | None): Summary of the parent element.
            - pass_number (int): The current pass number in multi-pass summarization.
            - previous_summary (str | None): The summary from the previous pass.

        Returns:
            - str: The created prompt.

        Raises:
            - Exception: If prompt creation fails.
        """
        prompt_creator: SummarizationPromptCreator = SummarizationPromptCreator()
        prompt: str | None = prompt_creator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
            parent_summary,
            pass_number,
            previous_summary,
        )

        if prompt:
            return prompt
        else:
            raise Exception("Prompt creation failed.")

    def _get_summary(
        self,
        messages: list[ChatCompletionMessageParam],
    ) -> OpenAIReturnContext | None:
        """
        Retrieves the summary from the OpenAI API based on the provided messages and configuration settings.

        Args:
            - messages (list[ChatCompletionMessageParam]): A list of messages for chat completion.

        Returns:
            OpenAIReturnContext | None: The summary generated by the OpenAI API, or None if no summary is found.
        """

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                messages=messages,
                model=self.configs.model,
                max_tokens=self.configs.max_tokens,
                temperature=self.configs.temperature,
            )
            prompt_tokens: int = 0
            completion_tokens: int = 0
            summary: str | None = response.choices[0].message.content
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens

            return OpenAIReturnContext(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                summary=summary,
            )

        except Exception as e:
            logging.error(e)
            return None

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
    ) -> OpenAIReturnContext | None:
        """
        Summarizes the provided code snippet using the OpenAI API.

        This method generates a summary of the given code, taking into account various contextual
        information such as children summaries, dependencies, imports, and parent summaries.
        It supports multi-pass summarization, allowing for refinement of summaries over multiple passes.

        Args:
            - code (str): The code snippet to summarize.
            - model_id (str): The identifier of the model being summarized.
            - children_summaries (str | None): Summaries of child elements, if any.
            - dependency_summaries (str | None): Summaries of dependencies, if any.
            - import_details (str | None): Details of imports used in the code.
            - parent_summary (str | None): Summary of the parent element, if applicable.
            - pass_number (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            - OpenAIReturnContext | None: A context object containing the summary and token usage information,
                                          or None if summarization fails.

        Example:
            ```Python
            summarizer = OpenAISummarizer()
            summary_context = summarizer.summarize_code(
                code="def greet(name):\n    return f'Hello, {name}!'",
                model_id="function_greet",
                children_summaries=None,
                dependency_summaries=None,
                import_details=None,
                parent_summary="Module with greeting functions",
                pass_number=2
            )
            if summary_context:
                print(f"Summary: {summary_context.summary}")
                print(f"Tokens used: {summary_context.prompt_tokens + summary_context.completion_tokens}")
            ```
        """

        logging.info(
            f"([blue]Pass {pass_number}[/blue]) - [green]Summarizing code for model:[/green] {model_id}"
        )
        prompt: str = self._create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
            parent_summary,
            pass_number,
            previous_summary,
        )
        messages: list[ChatCompletionMessageParam] = self._create_messages_list(
            system_message=self.configs.system_message, user_message=prompt
        )

        if summary_return_context := self._get_summary(messages):
            if summary_return_context.summary:
                summary_return_context.summary = summary_return_context.summary.split(
                    "FINAL SUMMARY:"
                )[-1].strip()
                return summary_return_context
        return None

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

        This method mimics the behavior of summarize_code but returns a predefined summary instead of
        making an actual API call. It's useful for testing the summarization pipeline without incurring
        API costs or when you want to test the surrounding logic.

        Args:
            - code (str): The code snippet to summarize (not used in the test method).
            - model_id (str): The identifier of the model being summarized.
            - children_summaries (str | None): Summaries of child elements, if any.
            - dependency_summaries (str | None): Summaries of dependencies, if any.
            - import_details (str | None): Details of imports used in the code.
            - parent_summary (str | None): Summary of the parent element, if applicable.
            - pass_number (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            - OpenAIReturnContext | None: A context object containing a test summary and token usage information.

        Example:
            ```Python
            summarizer = OpenAISummarizer()
            test_summary = summarizer.test_summarize_code(
                code="print('Hello, World!')",
                model_id="test_function",
                children_summaries=None,
                dependency_summaries=None,
                import_details=None,
                parent_summary="Test Module",
                pass_number=1
            )
            print(test_summary.summary if test_summary else "Test summarization failed")
            ```
        """

        summary = f"""\nTest Summary for {model_id}:\n
        Pass Number: {pass_number}
        Parent Summary: {parent_summary}
        Children Summaries: {children_summaries}
        Dependency Summaries: {dependency_summaries}
        Import Details: {import_details}
        """
        summary_context = OpenAIReturnContext(
            summary=summary,
            prompt_tokens=1,
            completion_tokens=1,
        )

        return summary_context
