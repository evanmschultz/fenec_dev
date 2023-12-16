import logging
from typing import Callable, LiteralString
import ai_services.prompts.summarization_prompts as prompts


class PromptCreator:
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
        prompt_string: str = prompt_template
        for key, value in kwargs.items():
            if value:
                prompt_string = prompt_string.replace(f"{{{key}}}", value)

        return prompt_string

    def create_prompt(
        self,
        code: str,
        children_summaries: str | None = None,
        dependency_summaries: str | None = None,
        import_details: str | None = None,
    ) -> str | None:
        strategy_key: LiteralString = "_".join(
            [
                "children" if children_summaries else "nochildren",
                "dependencies" if dependency_summaries else "nodependencies",
                "import_details" if import_details else "noimport_details",
            ]
        )
        strategy: Callable[..., str] | None = self._interpolation_strategies.get(
            strategy_key
        )
        if strategy:
            return strategy(
                code, children_summaries, dependency_summaries, import_details
            )
        else:
            raise ValueError(f"Could not find strategy for {strategy_key}")


def main() -> None:
    prompt_creator = PromptCreator()
    prompt_1: str | None = prompt_creator.create_prompt(
        code="example code",
        children_summaries="example children summaries",
        dependency_summaries="example dependencies",
        import_details="example import details",
    )
    print("Everything:\n")
    print(prompt_1, "\n")

    prompt_2: str | None = prompt_creator.create_prompt(
        code="example code",
        children_summaries="example children summaries",
        dependency_summaries="example dependencies",
    )
    print("No import details:\n")
    print(prompt_2, "\n")

    prompt_3: str | None = prompt_creator.create_prompt(
        code="example code",
        children_summaries="example children summaries",
        import_details="example import details",
    )
    print("No dependencies:\n")
    print(prompt_3, "\n")

    prompt_4: str | None = prompt_creator.create_prompt(
        code="example code",
        children_summaries="example children summaries",
    )
    print("No dependencies and no import details:\n")
    print(prompt_4, "\n")

    prompt_5: str | None = prompt_creator.create_prompt(
        code="example code",
        dependency_summaries="example dependencies",
        import_details="example import details",
    )
    print("No children:\n")
    print(prompt_5, "\n")

    prompt_6: str | None = prompt_creator.create_prompt(
        code="example code",
        dependency_summaries="example dependencies",
    )
    print("No children and no import details:\n")
    print(prompt_6, "\n")

    prompt_7: str | None = prompt_creator.create_prompt(
        code="example code",
        import_details="example import details",
    )
    print("No children and no dependencies:\n")
    print(prompt_7, "\n")

    prompt_8: str | None = prompt_creator.create_prompt(
        code="example code",
    )
    print("No children, no dependencies, and no import details:\n")
    print(prompt_8, "\n")


if __name__ == "__main__":
    main()
