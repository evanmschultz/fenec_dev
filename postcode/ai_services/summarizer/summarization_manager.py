import logging

from postcode.ai_services.summarizer.summarizer_protocol import Summarizer
from postcode.types.postcode import ModelType

from postcode.python_parser.models.models import (
    DependencyModel,
    ImportModel,
    ModuleModel,
)
import postcode.ai_services.summarizer.summarizer_context as context


class SummarizationManager:
    def __init__(
        self,
        module_models_tuple: tuple[ModuleModel, ...],
        summarizer: Summarizer,
    ) -> None:
        self.module_models_tuple: tuple[ModuleModel, ...] = module_models_tuple
        self.summarizer: Summarizer = summarizer
        self.summarized_code_block_ids: set[str] = set()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    @property
    def total_cost(self) -> float:
        prompt_cost: int = self.prompt_tokens * 1  # Costs 1 cent per 1,000 tokens
        completion_cost: int = (
            self.completion_tokens * 3
        )  # Costs 3 cents per 1,000 tokens
        return (prompt_cost + completion_cost) / 100_000  # Convert to dollars

    def create_and_add_summaries_to_models(self) -> None:
        for module_model in self.module_models_tuple:
            self._summarize_module(module_model)

    def _summarize_module(self, module_model: ModuleModel) -> None:
        if module_model.id not in self.summarized_code_block_ids:
            self._summarize_code_block(module_model)
            logging.info(f"Summarized module: {module_model.id}")
            self.summarized_code_block_ids.add(module_model.id)

    def _summarize_code_block(
        self,
        model: ModelType,
        recursion_path: list[str] = [],
    ) -> str | None:
        if model.id in recursion_path or not model.code_content:
            return None
        if model.id in self.summarized_code_block_ids:
            return model.summary

        recursion_path.append(model.id)

        child_summary_list: list[str] | None = None
        if model.children:
            child_summary_list = self._get_child_summaries(model, recursion_path)

        dependency_summary_list: list[str] = []
        import_details: str | None = None
        if model.dependencies:
            for dependency in model.dependencies:
                if isinstance(dependency, DependencyModel) and dependency.code_block_id:
                    if module_local_dependency_summary := self._get_local_dependency_summary(
                        dependency, model, recursion_path
                    ):
                        dependency_summary_list.append(module_local_dependency_summary)

                if isinstance(dependency, ImportModel):
                    if dependency.import_module_type == "LOCAL":
                        if not dependency.import_names:
                            if module_import_dependency := self._get_local_import_summary(
                                dependency, recursion_path
                            ):
                                dependency_summary_list.append(module_import_dependency)
                        else:
                            if import_from_dependency := self._get_local_import_from_summary(
                                dependency, recursion_path
                            ):
                                dependency_summary_list.append(import_from_dependency)
                    else:
                        import_detail: str | None = self._get_import_details(dependency)
                        if not import_detail:
                            continue
                        if not import_details:
                            import_details = ""
                        import_details += f"\n{import_detail}"

        if isinstance(model, ModuleModel) and recursion_path:
            dependency_summary_list, import_details = self._handle_module_model(
                model, recursion_path
            )

        children_summaries: str | None = self._stringify_child_summaries(
            child_summary_list
        )
        dependency_summaries: str | None = self._stringify_dependency_summaries(
            dependency_summary_list
        )

        summary_context: context.OpenAIReturnContext | str = (
            self.summarizer.test_summarize_code(
                model.code_content,
                model_id=model.id,
                children_summaries=children_summaries,
                dependency_summaries=dependency_summaries,
                import_details=import_details,
            )
        )

        if isinstance(summary_context, context.OpenAIReturnContext):
            if summary_context.summary:
                model.summary = summary_context.summary
                self.summarized_code_block_ids.add(model.id)
                recursion_path.remove(model.id)

                self.prompt_tokens += summary_context.prompt_tokens
                self.completion_tokens += summary_context.completion_tokens
                logging.info(f"Summarized code block: {model.id}")
                logging.info(f"Total cost: {self.total_cost}")

        return (
            summary_context.summary
            if isinstance(summary_context, context.OpenAIReturnContext)
            else summary_context
        )

    def _handle_module_model(
        self, model: ModuleModel, recursion_path: list[str]
    ) -> tuple[list[str], str | None]:
        dependency_summary_list: list[str] = []
        all_import_details: str | None = None
        if model.imports:
            for import_model in model.imports:
                if import_model.import_module_type == "LOCAL":
                    if not import_model.import_names:
                        if module_import := self._get_local_import_summary(
                            import_model, recursion_path
                        ):
                            dependency_summary_list.append(module_import)
                    else:
                        if import_from := self._get_local_import_from_summary(
                            import_model, recursion_path
                        ):
                            dependency_summary_list.append(import_from)
                else:
                    if import_details := self._get_import_details(import_model):
                        if not all_import_details:
                            all_import_details = ""
                        all_import_details += f"\n{import_details}"

        return dependency_summary_list, all_import_details

    def _get_import_details(self, import_model: ImportModel) -> str | None:
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

    def _get_child_summaries(
        self, model: ModelType, recursion_path: list[str]
    ) -> list[str]:
        child_summary_list: list[str] = []
        if model.children:
            for child_model in model.children:
                child_summary: str | None = self._summarize_code_block(
                    child_model,
                    recursion_path,
                )
                if child_summary:
                    child_summary_list.append(child_summary)
        return child_summary_list

    def _stringify_child_summaries(
        self, child_summary_list: list[str] | None
    ) -> str | None:
        if not child_summary_list:
            return None

        children_summaries: str = ""
        for child_summary in child_summary_list:
            children_summaries += f"\n{child_summary}"
        return children_summaries

    def _stringify_dependency_summaries(
        self, dependency_summary_list: list[str] | None
    ) -> str | None:
        if not dependency_summary_list:
            return None

        dependency_summaries: str = ""
        for dependency_summary in dependency_summary_list:
            dependency_summaries += f"\n{dependency_summary}"
        return dependency_summaries

    def _get_local_dependency_summary(
        self,
        dependency: DependencyModel,
        model: ModelType,
        recursion_path: list[str],
    ) -> str | None:
        if not model.children:
            return None

        for child_model in model.children:
            if child_model.id == dependency.code_block_id:
                return self._summarize_code_block(
                    child_model,
                    recursion_path,
                )

    def _get_local_import_summary(
        self, dependency: ImportModel, recursion_path: list[str]
    ) -> str | None:
        for module_model in self.module_models_tuple:
            if module_model.id == dependency.local_module_id:
                return self._summarize_code_block(
                    module_model,
                    recursion_path,
                )

    def _get_local_import_from_summary(
        self, dependency: ImportModel, recursion_path: list[str]
    ) -> str | None:
        for import_name in dependency.import_names:
            for module_model in self.module_models_tuple:
                if module_model.id == dependency.local_module_id:
                    if module_model.children:
                        for child_model in module_model.children:
                            if (
                                child_model.id == import_name.local_block_id
                                and child_model.id
                            ):
                                return self._summarize_code_block(
                                    child_model,
                                    recursion_path,
                                )
