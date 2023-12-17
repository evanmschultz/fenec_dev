from typing import Callable, LiteralString

from postcode.ai_services.summarizer.prompts import summarization_prompts as prompts


class PromptCreator:
    """
    Class for creating prompts for the summarizer.

    Methods:
        - `create_prompt`: Static method that creates a prompt for the summarizer.

    Examples:
        ```Python
        # Create a prompt
        prompt: str | None = PromptCreator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
        )
        ```
    """

    _interpolation_strategies: dict[str, Callable[..., str]] = {
        "children_dependencies_import_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_WITH_EVERYTHING,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            import_details=import_details,
        ),
        "children_dependencies_noimport_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_IMPORTS,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
        ),
        "children_nodependencies_import_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES,
            code=code,
            children_summaries=children_summaries,
            import_details=import_details,
        ),
        "children_nodependencies_noimport_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_IMPORTS,
            code=code,
            children_summaries=children_summaries,
        ),
        "nochildren_dependencies_import_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_CHILDREN,
            code=code,
            dependencies=dependencies,
            import_details=import_details,
        ),
        "nochildren_dependencies_noimport_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_CHILDREN_NO_IMPORTS,
            code=code,
            dependencies=dependencies,
        ),
        "nochildren_nodependencies_import_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_CHILDREN,
            code=code,
            import_details=import_details,
        ),
        "nochildren_nodependencies_noimport_details": lambda code, children_summaries, dependencies, import_details: PromptCreator._interpolate_prompt_string(
            prompts.COD_SUMMARIZATION_PROMPT_WITHOUT_ANYTHING,
            code=code,
        ),
    }

    @staticmethod
    def _interpolate_prompt_string(prompt_template: str, **kwargs) -> str:
        """Returns a prompt string with the provided values interpolated into the template."""

        prompt_string: str = prompt_template
        for key, value in kwargs.items():
            if value:
                prompt_string = prompt_string.replace(f"{{{key}}}", value)

        return prompt_string

    @staticmethod
    def create_prompt(
        code: str,
        children_summaries: str | None = None,
        dependency_summaries: str | None = None,
        import_details: str | None = None,
    ) -> str | None:
        """
        Dynamically creates a prompt for the summarizer based on the provided arguments.

        Args:
            - code (str): The code snippet to summarize.
            - children_summaries (str, optional): The summaries of the children of the code snippet.
            - dependency_summaries (str, optional): The summaries of the dependencies of the code snippet.
            - import_details (str, optional): The import details of the code snippet.

        Returns:
            - str: The prompt for the summarizer.

        Examples:
            ```Python
            # Create a prompt
            prompt: str | None = PromptCreator.create_prompt(
                code,
                children_summaries,
                dependency_summaries,
                import_details,
            )
            ```
        """

        strategy_key: LiteralString = "_".join(
            [
                "children" if children_summaries else "nochildren",
                "dependencies" if dependency_summaries else "nodependencies",
                "import_details" if import_details else "noimport_details",
            ]
        )
        strategy: Callable[
            ..., str
        ] | None = PromptCreator._interpolation_strategies.get(strategy_key)
        if strategy:
            return strategy(
                code, children_summaries, dependency_summaries, import_details
            )
        else:
            raise ValueError(f"Could not find strategy for {strategy_key}")
