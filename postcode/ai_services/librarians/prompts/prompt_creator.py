import postcode.ai_services.librarians.prompts.chroma_librarian_prompts as prompts


class ChromaLibrarianPromptCreator:
    """
    Class for creating prompts for the Chroma Librarian.

    Methods:
        - `create_prompt`: Static method that creates a prompt for the Chroma Librarian.

    Examples:
        ```Python
        # Create a prompt
        prompt: str | None = ChromaLibrarianPromptCreator.create_prompt(
            user_question,
            prompt_template,
            queries_count,
        )
        ```
    """

    @staticmethod
    def create_prompt(
        user_question: str,
        prompt_template: str = prompts.DEFAULT_CHROMA_LIBRARIAN_PROMPT,
        queries_count: int = 3,
    ) -> str:
        """
        Creates a prompt for the Chroma Librarian by interpolating the given prompt template with the given user question and queries count.

        Args:
            - user_question (str): The user's question.
            - prompt_template (str): The template to interpolate.
                - default: DEFAULT_CHROMA_LIBRARIAN_PROMPT defined in `chroma_librarian_prompts.py`.
            - queries_count (int): The number of queries to make.
                - default: 3
        """

        return prompt_template.format(
            user_question=user_question,
            prompt_template=prompt_template,
            queries_count=queries_count,
        )
