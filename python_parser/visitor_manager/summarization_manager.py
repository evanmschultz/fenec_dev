import logging
from typing import Union

from ai_services.summarizer_protocol import Summarizer

from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder
from model_builders.standalone_block_model_builder import (
    StandaloneBlockModelBuilder,
)
from models.models import DependencyModel, ImportModel


BuilderType = Union[
    ModuleModelBuilder,
    ClassModelBuilder,
    FunctionModelBuilder,
    StandaloneBlockModelBuilder,
]


class SummarizationManager:
    def __init__(
        self,
        module_builders_tuple: tuple[ModuleModelBuilder, ...],
        summarizer: Summarizer,
    ) -> None:
        self.module_builders_tuple: tuple[
            ModuleModelBuilder, ...
        ] = module_builders_tuple
        self.summarizer: Summarizer = summarizer
        self.summarized_code_block_ids: set[str] = set()

    def create_and_add_summaries_to_builders(self) -> None:
        for module_builder in self.module_builders_tuple:
            self._summarize_module(module_builder)

    def _summarize_module(self, module_builder: ModuleModelBuilder) -> None:
        if module_builder.id not in self.summarized_code_block_ids:
            self._summarize_code_block(module_builder)
            logging.info(f"Summarized module: {module_builder.id}")
            self.summarized_code_block_ids.add(module_builder.id)

    def _summarize_code_block(
        self,
        builder: BuilderType,
        recursion_path: list[str] = [],
    ) -> str | None:
        if builder.id in recursion_path or not builder.common_attributes.code_content:
            return None
        if builder.id in self.summarized_code_block_ids:
            return builder.common_attributes.summary

        recursion_path.append(builder.id)

        child_summary_list: list[str] | None = None
        if builder.children_builders:
            child_summary_list = self._get_child_summaries(builder, recursion_path)

        dependency_summary_list: list[str] = []
        import_details: str | None = None
        if builder.common_attributes.dependencies:
            for dependency in builder.common_attributes.dependencies:
                if isinstance(dependency, DependencyModel) and dependency.code_block_id:
                    if module_local_dependency_summary := self._get_local_dependency_summary(
                        dependency, builder, recursion_path
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

        if isinstance(builder, ModuleModelBuilder) and recursion_path:
            dependency_summary_list, import_details = self._handle_module_builder(
                builder, recursion_path
            )

        children_summaries: str | None = self._stringify_child_summaries(
            child_summary_list
        )
        dependency_summaries: str | None = self._stringify_dependency_summaries(
            dependency_summary_list
        )

        summary: str = self.summarizer.test_summarize_code(
            builder.common_attributes.code_content,
            builder_id=builder.id,
            children_summaries=children_summaries,
            dependency_summaries=dependency_summaries,
            import_details=import_details,
        )

        builder.add_summary(summary)
        self.summarized_code_block_ids.add(builder.id)
        recursion_path.remove(builder.id)

        return summary

    def _handle_module_builder(
        self, builder: ModuleModelBuilder, recursion_path: list[str]
    ) -> tuple[list[str], str | None]:
        dependency_summary_list: list[str] = []
        all_import_details: str | None = None
        if builder.module_attributes.imports:
            for import_model in builder.module_attributes.imports:
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
        self, builder: BuilderType, recursion_path: list[str]
    ) -> list[str]:
        child_summary_list: list[str] = []
        for child_builder in builder.children_builders:
            child_summary: str | None = self._summarize_code_block(
                child_builder,
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
        builder: BuilderType,
        recursion_path: list[str],
    ) -> str | None:
        for child_builder in builder.children_builders:
            if child_builder.id == dependency.code_block_id:
                return self._summarize_code_block(
                    child_builder,
                    recursion_path,
                )

    def _get_local_import_summary(
        self, dependency: ImportModel, recursion_path: list[str]
    ) -> str | None:
        for module_builder in self.module_builders_tuple:
            if module_builder.id == dependency.local_module_id:
                return self._summarize_code_block(
                    module_builder,
                    recursion_path,
                )

    def _get_local_import_from_summary(
        self, dependency: ImportModel, recursion_path: list[str]
    ) -> str | None:
        for import_name in dependency.import_names:
            for module_builder in self.module_builders_tuple:
                if module_builder.id == dependency.local_module_id:
                    for child_builder in module_builder.children_builders:
                        if (
                            child_builder.id == import_name.local_block_id
                            and child_builder.id
                        ):
                            return self._summarize_code_block(
                                child_builder,
                                recursion_path,
                            )
