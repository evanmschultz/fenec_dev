import logging
from typing import Sequence
from openai import OpenAI

from postcode.ai_services.openai_configs import OpenAIConfigs
import postcode.types.chroma as chroma_types
import postcode.types.openai as openai_types

from postcode.ai_services.librarians.chroma_librarians import ChromaLibrarian
from postcode.ai_services.chat.prompts.chat_prompts import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_SYSTEM_PROMPT,
)


class OpenAIChatAgent:
    """
    Represents an agent that interacts with the OpenAI API for generating responses to user questions.

    Args:
        - `chroma_librarian` (ChromaLibrarian): The librarian handling Chroma queries.
        - `configs` (OpenAIConfigs, optional): Configuration settings for the OpenAI agent.

    Methods:
        - `get_response`(user_question, prompt_template=DEFAULT_PROMPT_TEMPLATE):
            Generates a response to the user's question using the specified prompt template.



    Attributes:
        - `chroma_librarian` (ChromaLibrarian): The Chroma librarian instance.
        - `model` (str): The OpenAI model being used.
        - `client`: The OpenAI API client.
    """

    def __init__(
        self,
        chroma_librarian: ChromaLibrarian,
        configs: OpenAIConfigs = OpenAIConfigs(),
    ) -> None:
        self.chroma_librarian: ChromaLibrarian = chroma_librarian
        self.configs: OpenAIConfigs = configs
        self.client = OpenAI()

    def get_response(
        self, user_question: str, prompt_template: str = DEFAULT_PROMPT_TEMPLATE
    ) -> str | None:
        """
        Generates a response to the user's question using the OpenAI API.

        Args:
            - `user_question` (str): The user's question.
            - `prompt_template` (str, optional): The template for formatting the prompt.
                default: DEFAULT_PROMPT_TEMPLATE.

        Returns:
            - `str | None`: The generated response or None if the response could not be generated.

        Raises:
            - `ValueError`: If user_question is empty.
            - `RuntimeError`: If there is an issue with the OpenAI API request.
            - `KeyError`: If the prompt template is missing required keys.

        Example:
            ```python
            agent = OpenAIChatAgent(chroma_librarian, model="gpt-4o")
            try:
                response = agent.get_response("What code blocks use recursion?")
                print(response)
            except ValueError as ve:
                print(f"ValueError: {ve}")
            except RuntimeError as re:
                print(f"RuntimeError: {re}")
            except KeyError as ke:
                print(f"KeyError: {ke}")
            ```
        """
        if not user_question:
            raise ValueError("User question cannot be empty.")

        try:
            chroma_results: chroma_types.QueryResult | None = (
                self.chroma_librarian.query_chroma(user_question)
            )

            if not chroma_results:
                return "I don't know how to answer that question."

            documents: list[list[str]] | None = chroma_results["documents"]

            if not documents:
                return "I don't know how to answer that question."

            context: str = ""
            for document in documents:
                context += "\n".join(document) + "\n"

            prompt: str = self._format_prompt(context, user_question, prompt_template)

            messages: Sequence[dict[str, str]] = [
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            response: openai_types.ChatCompletion = self.client.chat.completions.create(
                model=self.configs.model,
                messages=messages,  # type: ignore # FIXME: fix type hinting error
                temperature=self.configs.temperature,
                # response_format={"type": "json_object"},
            )
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Error interacting with OpenAI API: {e}") from e

    def _format_prompt(
        self,
        context: str,
        user_question: str,
        prompt_template: str,
    ) -> str:
        """
        Formats the prompt for the OpenAI API based on the provided context, user's question, and template.

        Args:
            - `context` (str): The context derived from Chroma query results.
            - `user_question` (str): The user's question.
            - `prompt_template` (str): The template for formatting the prompt.

        Returns:
            - `str`: The formatted prompt.

        Raises:
            - `KeyError`: If the prompt template is missing required keys.

        Example:
            ```python
            prompt = agent._format_prompt("Context here", "What is the meaning of life?", "Template {context} {user_question}")
            print(prompt)
            ```
        """

        try:
            return prompt_template.format(context=context, user_question=user_question)

        except KeyError as e:
            raise KeyError(f"Prompt template is missing the following key: {e}") from e
