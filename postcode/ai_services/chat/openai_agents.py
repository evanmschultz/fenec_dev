import logging
from typing import Sequence
from openai import OpenAI

import postcode.types.chroma as chroma_types
import postcode.types.openai as openai_types

from postcode.ai_services.librarians.chroma_librarians import ChromaLibrarian
from postcode.ai_services.chat.prompts.prompts import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_SYSTEM_PROMPT,
)


class OpenAIChatAgent:
    def __init__(
        self,
        chroma_librarian: ChromaLibrarian,
        model: str = "gpt-4-1106-preview",
    ) -> None:
        self.chroma_librarian: ChromaLibrarian = chroma_librarian
        self.model: str = model
        self.client = OpenAI()

    def get_response(
        self, user_question: str, prompt_template: str = DEFAULT_PROMPT_TEMPLATE
    ) -> str | None:
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
            model=self.model,
            messages=messages,  # type: ignore # FIXME: fix type hinting error
            temperature=0.1,
            # response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _format_prompt(
        self,
        context: str,
        user_question: str,
        prompt_template: str,
    ) -> str:
        try:
            return prompt_template.format(context=context, user_question=user_question)

        except KeyError as e:
            raise KeyError(f"Prompt template is missing the following key: {e}") from e
