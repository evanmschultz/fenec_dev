import logging
import json

from openai import OpenAI
from pydantic import BaseModel
import postcode.types.openai as openai_types
from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)
from postcode.ai_services.librarians.prompts.prompt_creator import (
    ChromaLibrarianPromptCreator,
)
from postcode.ai_services.librarians.prompts.chroma_librarian_prompts import (
    DEFAULT_CHROMA_LIBRARIAN_PROMPT,
    DEFAULT_CHROMA_LIBRARIAN_SYSTEM_PROMPT,
)
import postcode.types.chroma as chroma_types

# TOOLS: list[dict[str, Any]] = [
#     {
#         "type": "function",
#         "function": {
#             "name": "query_chroma",
#             "description": "Get the results from the chromadb vector database using a list of queries.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "queries": {
#                         "type": "list[str]",
#                         "description": "List of queries to use to get the results from the chromadb vector database.",
#                     },
#                     "n_results": {
#                         "type": "int",
#                         "description": "Number of results to return, default is 10.",
#                     },
#                 },
#                 "required": ["queries"],
#             },
#         },
#     }
# ]


class OpenAIResponseContent(BaseModel):
    query_list: list[str]


class ChromaLibrarian:
    def __init__(
        self,
        collection_manager: ChromaCollectionManager,
        model: str = "gpt-3.5-turbo-1106",
    ) -> None:
        self.collection_manager: ChromaCollectionManager = collection_manager
        self.model: str = model
        self.client = OpenAI()

    def query_chroma(self, user_question: str) -> chroma_types.QueryResult | None:
        queries: list[str] | None = self._get_chroma_queries(user_question)
        if not queries:
            return None

        print(queries)

        return self._query_collection(queries)

    def _query_collection(
        self,
        queries: list[str],
        n_results: int = 3,
    ) -> chroma_types.QueryResult | None:
        return self.collection_manager.query_collection(
            queries,
            n_results=n_results,
            include_in_result=["metadatas", "documents"],
        )

    def _get_chroma_queries(
        self, user_question: str, queries_count: int = 3, retries: int = 3
    ) -> list[str] | None:
        while retries > 0:
            retries -= 1

            prompt: str = ChromaLibrarianPromptCreator.create_prompt(
                user_question,
                prompt_template=DEFAULT_CHROMA_LIBRARIAN_PROMPT,
                queries_count=queries_count,
            )

            try:
                completion: openai_types.ChatCompletion = (
                    self.client.chat.completions.create(
                        model=self.model,
                        response_format={"type": "json_object"},
                        messages=[
                            {
                                "role": "system",
                                "content": DEFAULT_CHROMA_LIBRARIAN_SYSTEM_PROMPT,
                            },
                            {"role": "user", "content": prompt},
                        ],
                    )
                )
                content: str | None = completion.choices[0].message.content
                if not content:
                    continue

                content_json = json.loads(content)
                content_model = OpenAIResponseContent(
                    query_list=content_json["query_list"]
                )
                print(content_model)

                if content:
                    queries: list[str] = content_model.query_list
                    if queries and len(queries) == queries_count:
                        return queries

            except Exception as e:
                logging.error(f"An error occurred: {e}")

        return None

    # def get_chroma_queries(
    #     self, user_question: str, queries_count: int = 3, retries: int = 3
    # ) -> list[str] | None:
    #     if retries < 1:
    #         return None

    #     prompt: str = ChromaLibrarianPromptCreator.create_prompt(
    #         user_question,
    #         prompt_template=DEFAULT_CHROMA_LIBRARIAN_PROMPT,
    #         queries_count=queries_count,
    #     )

    #     completion: openai_types.ChatCompletion = self.client.chat.completions.create(
    #         model=self.model,
    #         messages=[
    #             {"role": "system", "content": DEFAULT_CHROMA_LIBRARIAN_SYSTEM_PROMPT},
    #             {"role": "user", "content": prompt},
    #         ],
    #     )
    #     content: str | None = completion.choices[0].message.content
    #     if not content:
    #         return self.get_chroma_queries(user_question, queries_count, retries - 1)

    #     queries: str = content.split("QUERIES_LIST:")[-1]
    #     if len(queries) < 1:
    #         return self.get_chroma_queries(user_question, queries_count, retries - 1)

    #     return queries.strip("[]").split(", ")
