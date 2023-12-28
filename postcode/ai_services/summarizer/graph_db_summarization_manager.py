import logging
from typing import Union

from postcode.ai_services.summarizer.summarization_context import (
    Summarizer,
    OpenAIReturnContext,
)
from postcode.ai_services.summarizer.summarization_mapper import SummarizationMapper

# from postcode.types.postcode import ModelType

from postcode.models.models import (
    ClassModel,
    DependencyModel,
    FunctionModel,
    ImportModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]


class GraphDBSummarizationManager:
    def __init__(
        self,
        module_models_tuple: tuple[ModuleModel, ...],
        summarization_mapper: SummarizationMapper,
        summarizer: Summarizer,
    ) -> None:
        self.module_models_tuple: tuple[ModuleModel, ...] = module_models_tuple
        self.summarization_mapper: SummarizationMapper = summarization_mapper
        self.summarizer: Summarizer = summarizer
        self.summarized_code_block_ids: set[str] = set()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    @property
    def total_cost(self) -> float:
        """Provides the total cost of the summarization process."""
        prompt_cost: int = self.prompt_tokens * 1  # Costs 1 cent per 1,000 tokens
        completion_cost: int = (
            self.completion_tokens * 3
        )  # Costs 3 cents per 1,000 tokens
        return (prompt_cost + completion_cost) / 100_000  # Convert to dollars

    def create_summaries_and_return_updated_models(self) -> tuple[ModuleModel, ...]:
        summarization_map: list[
            ModelType
        ] = self.summarization_mapper.create_summarization_map()
        models_to_summarize_count: int = len(summarization_map)
        models_summarized_count: int = 0

        for model in summarization_map:
            children_summaries: str | None = None
            dependency_summaries: str | None = None
            import_details: str | None = None

            if model.children:
                children_summaries: str | None = self._stringify_children_summaries(
                    self._get_child_summaries(model)
                )
            if isinstance(model, ModuleModel):
                if model.imports:
                    dependency_summaries = self._get_dependencies_summaries(model)
                    import_details = ""
                    for _import in model.imports:
                        if import_summary := self._get_import_details(_import):
                            import_details += f"\n{import_summary}"
            else:
                if model.dependencies:
                    dependency_summaries = self._get_dependencies_summaries(model)
                    import_details = ""
                    for dependency in model.dependencies:
                        if isinstance(dependency, DependencyModel):
                            continue
                        if import_summary := self._get_import_details(dependency):
                            import_details += f"\n{import_summary}"

            models_summarized_count += 1
            logging.info(
                f"Summarizing model {models_summarized_count} out of {models_to_summarize_count}; {model.id}."
            )

            summary_return_context: OpenAIReturnContext | None = (
                self.summarizer.test_summarize_code(
                    model.code_content,
                    model_id=model.id,
                    children_summaries=children_summaries,
                    dependency_summaries=dependency_summaries,
                    import_details=import_details,
                )
            )
            if summary_return_context:
                model.summary = summary_return_context.summary
                self.prompt_tokens += summary_return_context.prompt_tokens
                self.completion_tokens += summary_return_context.completion_tokens

                for module_model in self.module_models_tuple:
                    if isinstance(model, ModuleModel):
                        if module_model.id == model.id:
                            module_model.summary = model.summary
                            break
                        else:
                            continue
                    else:
                        module_id_for_model: str = model.id.split("MODULE")[0]
                        if (
                            module_model.children
                            and module_id_for_model in module_model.id
                        ):
                            for child_model in module_model.children:
                                if child_model.id == model.id:
                                    child_model.summary = model.summary
                                    break
                        else:
                            continue

        return self.module_models_tuple

    def _get_child_summaries(self, model: ModelType) -> list[str]:
        """Gathers summaries of child models."""
        child_summary_list: list[str] = []
        if model.children:
            for child in model.children:
                if child.summary:
                    child_summary: str = child.summary
                else:
                    child_summary = (
                        f"Child ({child.id}) code content:\n{child.code_content}\n"
                    )
                child_summary_list.append(child_summary)
        return child_summary_list

    def _stringify_children_summaries(self, children_summary_list: list[str]) -> str:
        """Converts all of the child summaries to a single string to be used in the prompt."""

        children_summaries: str = ""
        for child_summary in children_summary_list:
            children_summaries += f"\n{child_summary}"
        return children_summaries

    def _get_dependencies_summaries(self, model: ModelType) -> str | None:
        dependency_list: list[ImportModel | DependencyModel] | list[ImportModel] = []
        dependency_summary_list: list[str] = []

        if isinstance(model, ModuleModel):
            if not model.imports:
                return None

            dependency_list = model.imports
        else:
            if not model.dependencies:
                return None

            dependency_list = model.dependencies
        for dependency in dependency_list:
            if isinstance(dependency, DependencyModel) and dependency.code_block_id:
                if module_local_dependency_summary := self._get_local_dependency_summary(
                    dependency, model
                ):
                    dependency_summary_list.append(module_local_dependency_summary)

            elif isinstance(dependency, ImportModel):
                if dependency.import_module_type == "LOCAL":
                    if not dependency.import_names:
                        if module_import_dependency := self._get_local_import_summary(
                            dependency
                        ):
                            dependency_summary_list.append(module_import_dependency)
                    else:
                        if import_from_dependency := self._get_local_import_from_summary(
                            dependency
                        ):
                            dependency_summary_list.append(import_from_dependency)

        dependency_summaries = self._stringify_dependencies_summaries(
            dependency_summary_list
        )

        return dependency_summaries

    # def _get_import_details_for_dependencies(
    #     self, dependencies: list[ImportModel | DependencyModel]
    # ) -> str | None:
    #     import_details: str | None = None
    #     for dependency in dependencies:
    #         if isinstance(dependency, ImportModel):
    #             if dependency.import_module_type == "LOCAL":
    #                 continue
    #             else:
    #                 import_detail: str | None = self._get_import_details(dependency)
    #                 if not import_detail:
    #                     continue
    #                 if not import_details:
    #                     import_details = ""
    #                 import_details += f"\n{import_detail}"
    #     return import_details

    def _get_local_dependency_summary(
        self,
        dependency: DependencyModel,
        model: ModelType,
    ) -> str | None:
        """Gets a summary for a dependency local to the module."""
        if not model.children:
            return None

        for child_model in model.children:
            if child_model.id == dependency.code_block_id:
                child_summary: str | None = None

                if child_model.summary:
                    child_summary = child_model.summary
                else:
                    child_summary = f"Dependency ({dependency.code_block_id}) code content:\n{child_model.code_content}\n"

                return child_summary
        return None

    def _stringify_dependencies_summaries(
        self, dependencies_summary_list: list[str] | None
    ) -> str | None:
        """Converts all of the dependency summaries to a single string to be used in the prompt."""
        if not dependencies_summary_list:
            return None

        dependency_summaries: str = ""
        for dependency_summary in dependencies_summary_list:
            dependency_summaries += f"\n{dependency_summary}"
        return dependency_summaries

    def _get_local_import_summary(self, dependency: ImportModel) -> str | None:
        for module_model in self.module_models_tuple:
            if module_model.id == dependency.local_module_id:
                import_summary: str | None = None
                if module_model.summary:
                    import_summary = module_model.summary
                else:
                    import_summary = f"Imported module ({dependency.local_module_id}) code content:\n{module_model.code_content}\n"
                return import_summary
        return None

    def _get_local_import_from_summary(self, dependency: ImportModel) -> str | None:
        for import_name in dependency.import_names:
            for module_model in self.module_models_tuple:
                if module_model.id == dependency.local_module_id:
                    if module_model.children:
                        for child_model in module_model.children:
                            if (
                                child_model.id == import_name.local_block_id
                                and child_model.id
                            ):
                                import_summary: str | None = None
                                if child_model.summary:
                                    import_summary = child_model.summary
                                else:
                                    import_summary = f"Imported code block ({dependency.local_module_id}) code content:\n{module_model.code_content}\n"
                                return import_summary
        return None

    def _get_import_details(self, import_model: ImportModel) -> str | None:
        """Retrieves details of import statements to be used in the prompt."""
        if import_model.import_module_type == "LOCAL" or not import_model.import_names:
            return None

        import_names_list: list[str] = []
        for import_name in import_model.import_names:
            if import_name.as_name:
                import_names_list.append(f"{import_name.name} as {import_name.as_name}")
            else:
                import_names_list.append(f"{import_name.name}")

        if import_model.imported_from:
            import_details: str = f"from {import_model.imported_from} import {', '.join(import_names_list)}"
        else:
            import_details = f"import {', '.join(import_names_list)}"

        return import_details
