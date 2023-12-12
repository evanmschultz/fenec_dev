from typing import Union
from ai_services.summarizer import Summarizer
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
            self._summarize_code_block(module_builder, recursion_path=None)
            self.summarized_code_block_ids.add(module_builder.id)

    def _summarize_code_block(
        self,
        builder: BuilderType,
        *,
        recursion_path: list[str] | None,
        prev_builder: BuilderType | None = None,
    ) -> BuilderType | None:
        recursion_path = recursion_path if recursion_path else []

        if builder.id in self.summarized_code_block_ids or builder.id in recursion_path:
            return None

        recursion_path.append(builder.id)

        if builder.children_builders or builder.common_attributes.dependencies:
            if builder.children_builders:
                self._handle_children_builders(builder)

            if builder.common_attributes.dependencies:
                for dependency in builder.common_attributes.dependencies:
                    if (
                        isinstance(dependency, DependencyModel)
                        and dependency.code_block_id
                        not in self.summarized_code_block_ids
                    ):
                        self._handle_local_dependency(dependency, builder)

                    if isinstance(dependency, ImportModel):
                        if not dependency.import_names:
                            self._handle_import_dependency(
                                dependency, builder, recursion_path
                            )
                        else:
                            self._handle_import_from_dependency(
                                dependency, builder, recursion_path
                            )

        # summary: str = self.summarizer.summarize_code(
        #     builder.common_attributes.code_content
        # )
        summary: str = "summary complete"
        builder.add_summary(summary)
        self.summarized_code_block_ids.add(builder.id)
        recursion_path.remove(builder.id)

        return prev_builder if prev_builder else None

    def _handle_children_builders(self, builder: BuilderType) -> None:
        for child_builder in builder.children_builders:
            if child_builder.id not in self.summarized_code_block_ids:
                self._summarize_code_block(
                    child_builder, prev_builder=builder, recursion_path=None
                )

    def _handle_local_dependency(
        self, dependency: DependencyModel, builder: BuilderType
    ) -> None:
        for child_builder in builder.children_builders:
            if child_builder.id == dependency.code_block_id:
                self._summarize_code_block(
                    child_builder,
                    prev_builder=builder,
                    recursion_path=None,
                )

    def _handle_import_dependency(
        self, dependency: ImportModel, builder: BuilderType, recursion_path: list[str]
    ) -> None:
        for module_builder in self.module_builders_tuple:
            if (
                module_builder.id == dependency.local_module_id
                and module_builder.id not in self.summarized_code_block_ids
            ):
                self._summarize_code_block(
                    module_builder,
                    prev_builder=builder,
                    recursion_path=recursion_path,
                )

    def _handle_import_from_dependency(
        self, dependency: ImportModel, builder: BuilderType, recursion_path: list[str]
    ) -> None:
        for import_name in dependency.import_names:
            if import_name.local_block_id not in self.summarized_code_block_ids:
                for module_builder in self.module_builders_tuple:
                    if module_builder.id == dependency.local_module_id:
                        for child_builder in module_builder.children_builders:
                            if (
                                child_builder.id == import_name.local_block_id
                                and child_builder.id
                                not in self.summarized_code_block_ids
                            ):
                                self._summarize_code_block(
                                    child_builder,
                                    prev_builder=builder,
                                    recursion_path=recursion_path,
                                )
