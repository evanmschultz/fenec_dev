import logging
import re
from typing import Callable

from rich import print

import postcode.ai_services.summarizer.prompts.summarization_prompts as prompts


class SummarizationPromptCreator:
    """
    Class for creating prompts for the summarizer, supporting multi-pass summarization.

    Methods:
        - `create_prompt`: Static method that creates a prompt for the summarizer.

    Examples:
        ```Python
        # Create a prompt for single-pass summarization
        prompt: str | None = SummarizationPromptCreator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
        )

        # Create a prompt for multi-pass summarization
        prompt: str | None = SummarizationPromptCreator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
            parent_summary,
            pass_number=2,
            previous_summary="Previous summary of the code."
        )
        ```
    """

    _interpolation_strategies: dict[str, Callable[..., str]] = {
        # Pass 1 strategies (unchanged)
        "children_dependencies_import_details_parent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            import_details=import_details,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_dependencies_noimport_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_import_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            children_summaries=children_summaries,
            import_details=import_details,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_noimport_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            children_summaries=children_summaries,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_import_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            dependencies=dependencies,
            import_details=import_details,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_noimport_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            dependencies=dependencies,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_import_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            import_details=import_details,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_noimport_details_noparent_pass1": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_1,
            code=code,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        # Pass 2 strategies (updated to include previous_summary)
        "children_dependencies_import_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_dependencies_noimport_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_import_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_noimport_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_import_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            dependencies=dependencies,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_noimport_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            dependencies=dependencies,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_import_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_noimport_details_parent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_noimport_details_noparent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_dependencies_noimport_details_noparent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_noimport_details_noparent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            dependencies=dependencies,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_noimport_details_noparent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        # Pass 3 strategies (updated to include previous_summary)
        "children_dependencies_import_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_dependencies_noimport_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_import_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            children_summaries=children_summaries,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_noimport_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            children_summaries=children_summaries,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_dependencies_noimport_details_noparent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            children_summaries=children_summaries,
            dependencies=dependencies,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_import_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            dependencies=dependencies,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_noimport_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            dependencies=dependencies,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_dependencies_noimport_details_noparent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            dependencies=dependencies,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_import_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            import_details=import_details,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_noimport_details_parent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            parent_summary=parent_summary,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "nochildren_nodependencies_noimport_details_noparent_pass3": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_3,
            code=code,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
        "children_nodependencies_noimport_details_noparent_pass2": lambda code, children_summaries, dependencies, import_details, parent_summary, pass_number, previous_summary: SummarizationPromptCreator._interpolate_prompt_string(
            prompts.CODE_SUMMARY_PROMPT_PASS_2,
            code=code,
            children_summaries=children_summaries,
            previous_summary=previous_summary,
            EXAMPLE_1=prompts.EXAMPLE_1,
            EXAMPLE_2=prompts.EXAMPLE_2,
        ),
    }

    @staticmethod
    def _interpolate_prompt_string(prompt_template: str, **kwargs) -> str:
        """
        Returns a prompt string with the provided values interpolated into the template
        and all traces of unused placeholders removed.

        Args:
            - `prompt_template` (str): The template string to interpolate.
            - `**kwargs`: Keyword arguments containing the values to interpolate.

        Returns:
            - `str`: The interpolated prompt string with all traces of unused placeholders removed.
        """

        prompt_string: str = prompt_template

        # First, replace all provided values
        for key, value in kwargs.items():
            if value is not None:
                placeholder: str = f"{{{key}}}"
                prompt_string = prompt_string.replace(placeholder, str(value))

        # Remove lines containing unused placeholders and their associated labels
        lines: list[str] = prompt_string.split("\n")
        cleaned_lines: list[str] = []
        skip_next = False
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue

            # Check if the line or the next line contains an unused placeholder
            current_line_has_placeholder = re.search(r"\{[^}]+\}", line)
            next_line_has_placeholder = i + 1 < len(lines) and re.search(
                r"\{[^}]+\}", lines[i + 1]
            )

            if current_line_has_placeholder or next_line_has_placeholder:
                # If this line is a label and the next line is an unused placeholder, skip both
                if not current_line_has_placeholder and next_line_has_placeholder:
                    skip_next = True
                continue

            # Keep lines without unused placeholders
            cleaned_lines.append(line)

        cleaned_prompt: str = "\n".join(cleaned_lines)
        cleaned_prompt = re.sub(r"\n\s*\n", "\n\n", cleaned_prompt).strip()
        # print(
        #     f"\n\n[u][blue]Prompt:[/blue][/u]\n\n{cleaned_prompt}\n\n[u][magenta]End Prompt[/magenta][/u]\n\n"
        # )

        return cleaned_prompt

    @staticmethod
    def create_prompt(
        code: str,
        children_summaries: str | None = None,
        dependency_summaries: str | None = None,
        import_details: str | None = None,
        parent_summary: str | None = None,
        pass_number: int = 1,
        previous_summary: str | None = None,
    ) -> str | None:
        """
        Dynamically creates a prompt for the summarizer based on the provided arguments, supporting multi-pass summarization.

        Args:
            - `code` (str): The code snippet to summarize.
            - `children_summaries` (str, optional): The summaries of the children of the code snippet.
            - `dependency_summaries` (str, optional): The summaries of the dependencies of the code snippet.
            - `import_details` (str, optional): The import details of the code snippet.
            - `parent_summary` (str, optional): The summary of the parent code block (for multi-pass summarization).
            - `pass_number` (int, optional): The current pass number in multi-pass summarization. Default is 1.
            - `previous_summary` (str, optional): The summary from the previous pass in multi-pass summarization.

        Returns:
            - `str`: The prompt for the summarizer.

        Raises:
            - `ValueError`: If no strategy is found for the given combination of arguments.

        Examples:
            ```Python
            # Create a prompt for single-pass summarization
            prompt: str | None = SummarizationPromptCreator.create_prompt(
                code,
                children_summaries,
                dependency_summaries,
                import_details,
            )

            # Create a prompt for multi-pass summarization (e.g., second pass)
            prompt: str | None = SummarizationPromptCreator.create_prompt(
                code,
                children_summaries,
                dependency_summaries,
                import_details,
                parent_summary,
                pass_number=2,
                previous_summary="Previous summary of the code."
            )
            ```
        """

        strategy_key: str = "_".join(
            [
                "children" if children_summaries else "nochildren",
                "dependencies" if dependency_summaries else "nodependencies",
                "import_details" if import_details else "noimport_details",
                "parent" if parent_summary else "noparent",
                f"pass{pass_number}",
            ]
        )
        strategy: Callable[..., str] | None = (
            SummarizationPromptCreator._interpolation_strategies.get(strategy_key)
        )
        if not strategy:
            raise ValueError(f"Could not find strategy for {strategy_key}")
        else:
            # logging.info(f"Using strategy: {strategy_key}")
            # print(
            #     f"With children_summaries: {children_summaries}\n dependency_summaries: {dependency_summaries}\n "
            #     f"import_details: {import_details}\n parent_summary: {parent_summary}\n pass_number: {pass_number}\n "
            #     f"previous_summary: {previous_summary}"
            # )
            return strategy(
                code,
                children_summaries,
                dependency_summaries,
                import_details,
                parent_summary,
                pass_number,
                previous_summary,
            )
