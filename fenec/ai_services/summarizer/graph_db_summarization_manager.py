# TODO: Add logic to gather all child summaries of a directory (modules and directories within the directory)

import logging
from rich import print

from fenec.utilities.configs.configs import OpenAIReturnContext
from fenec.ai_services.summarizer.summarizer_protocol import Summarizer
from fenec.ai_services.summarizer.openai_summarizer import OpenAISummarizer
from fenec.ai_services.summarizer.ollama_summarizer import OllamaSummarizer
from fenec.ai_services.summarizer.summarization_mapper import SummarizationMapper
from fenec.databases.arangodb.arangodb_manager import ArangoDBManager

from fenec.types.fenec import ModelType

from fenec.models.models import (
    ClassModel,
    DependencyModel,
    DirectoryModel,
    FunctionModel,
    ImportModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)


class GraphDBSummarizationManager:
    """
    A class for managing summarization of models in a graph database.

    This class handles the process of summarizing code models, including support for multi-pass summarization.
    It interacts with a graph database to store and retrieve model information and summaries.

    Args:
        - `all_models_tuple` (tuple[ModelType, ...]): Tuple of all models available for summarization.
        - `summarization_mapper` (SummarizationMapper): The SummarizationMapper instance for creating summarization maps.
        - `summarizer` (Summarizer): The Summarizer instance for generating code summaries.
        - `graph_manager` (ArangoDBManager): The ArangoDBManager instance for handling database interactions.

    Properties:
        - `total_cost` (float): Provides the total cost of the summarization process.

    Methods:
        - `create_summaries_and_return_updated_models`(num_passes: int = 1): Creates summaries and updates models in the graph database.

    Example:
        ```python
        # Instantiate GraphDBSummarizationManager
        summarization_manager = GraphDBSummarizationManager(
            all_models_tuple=(ModuleModel(id="module_1"), FunctionModel(id="function_1")),
            summarization_mapper=my_summarization_mapper_instance,
            summarizer=my_summarizer_instance,
            graph_manager=my_arangodb_manager_instance
        )

        # Create summaries and update models with multi-pass summarization
        updated_models = summarization_manager.create_summaries_and_return_updated_models(num_passes=3)
        ```
    """

    def __init__(
        self,
        all_models_tuple: tuple[ModelType, ...],
        summarization_mapper: SummarizationMapper,
        summarizer: Summarizer,
        graph_manager: ArangoDBManager,
    ) -> None:
        self.all_models_tuple: tuple[ModelType, ...] = all_models_tuple
        self.summarization_mapper: SummarizationMapper = summarization_mapper
        self.summarizer: Summarizer = summarizer
        self.graph_manager: ArangoDBManager = graph_manager

        self.summarized_code_block_ids: set[str] = set()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    @property
    def total_cost(self) -> float:
        """Provides the total cost of the summarization process."""
        gpt_4o_2024_08_06_prompt_cost_per_token: float = 0.0000025
        prompt_cost: float = self.prompt_tokens * gpt_4o_2024_08_06_prompt_cost_per_token
        gpt_4o_2024_08_06_completion_cost_per_token: float = gpt_4o_2024_08_06_prompt_cost_per_token * 4
        completion_cost: float = (
            self.completion_tokens * gpt_4o_2024_08_06_completion_cost_per_token
        )  
        return (prompt_cost + completion_cost) 

    def create_summaries_and_return_updated_models(
        self, num_passes: int = 1
    ) -> list[ModelType] | None:
        """
        Creates summaries and updates models in the graph database.

        This method supports both single-pass and multi-pass summarization. In multi-pass mode,
        it performs bottom-up, top-down, and final bottom-up passes to create comprehensive summaries.

        Args:
            - `num_passes` (int): Number of summarization passes to perform. Must be either 1 or 3. Default is 1.

        Returns:
            - `list[ModelType] | None`: Updated models in the graph database or None if graph_manager is not provided.

        Raises:
            - `ValueError`: If num_passes is not 1 or 3.
        """
        if num_passes not in [1, 3]:
            raise ValueError("Number of passes must be either 1 or 3")

        return self._handle_summarization_passes(num_passes)

    def _handle_summarization_passes(
        self, num_of_passes: int
    ) -> list[ModelType] | None:
        if num_of_passes == 1:
            logging.info("Starting single-pass summarization")
            models: (
                list[
                    ModuleModel
                    | ClassModel
                    | FunctionModel
                    | StandaloneCodeBlockModel
                    | DirectoryModel
                ]
                | None
            ) = self._process_summarization_map(
                self.summarization_mapper.create_bottom_up_summarization_map(1), 1
            )

        else:
            logging.info("Starting multi-pass summarization")

            for pass_num in range(1, num_of_passes + 1):
                if pass_num % 2 != 0:
                    logging.info(f"[blue]Pass number:[/blue] {pass_num} (bottom-up)")
                    models = self._process_summarization_map(
                        self.summarization_mapper.create_bottom_up_summarization_map(
                            pass_num
                        ),
                        pass_num,
                    )
                else:
                    logging.info(f"[blue]Pass number:[/blue] {pass_num} (top-down)")
                    models = self._process_summarization_map(
                        self.summarization_mapper.create_top_down_summarization_map(
                            pass_num
                        ),
                        pass_num,
                        models,
                        top_down=True,
                    )
                self.summarization_mapper.model_visited_in_db = set()

        return models

    def _process_summarization_map(
        self,
        summarization_map: list[ModelType],
        pass_number: int,
        models: list[ModelType] | None = None,
        top_down: bool = False,
    ) -> list[ModelType] | None:
        """
        Processes a summarization map to create or update summaries for models.

        Args:
            - `summarization_map` (list[ModelType]): The map of models to summarize.
            - `pass_number` (int): The current summarization pass number.
            - `models` (list[ModelType] | None): Previously summarized models (if any).
            - `top_down` (bool): Whether this is a top-down summarization pass.

        Returns:
            - `list[ModelType] | None`: Updated list of models with new summaries.
        """
        models_to_summarize_count: int = len(summarization_map)
        models_summarized_count: int = 0

        for model in summarization_map:
            models_summarized_count += 1
            if isinstance(model, ImportModel):
                import_details = self._get_import_details(model)
            else:
                import_details = None
            logging.info(
                f"Summarizing model {models_summarized_count} out of {models_to_summarize_count}; {model.id}."
            )

            # Check if the model is an instance of ImportModel before calling _get_import_details
            if isinstance(model, ImportModel):
                import_details = self._get_import_details(model)

            children_summaries: str | None = self._get_child_summaries(model)
            dependency_summaries: str | None = self._get_dependencies_summaries(model)

            parent_summary: str | None = None
            if top_down and models:
                parent_model = next(
                    (m for m in models if m.id == model.parent_id), None
                )
                if parent_model:
                    parent_summary = parent_model.summary

            code_content: str = (
                model.code_content if not isinstance(model, DirectoryModel) else ""
            )

            previous_summary: str | None = None
            if not pass_number == 1:
                previous_summary = model.summary

            if isinstance(self.summarizer, OllamaSummarizer):
                model_summary: str | None = self.summarizer.summarize_code(
                    code_content,
                    model_id=model.id,
                    children_summaries=children_summaries,
                    dependency_summaries=dependency_summaries,
                    import_details=import_details,
                    parent_summary=parent_summary,
                    pass_number=pass_number,
                    previous_summary=previous_summary,
                )
                if model_summary:
                    stripped_summary: str = model_summary.strip()
                    print(f"[blue]Summary: [/blue]{stripped_summary}")
                    self.graph_manager.update_vertex_summary_by_id(
                        model.id, stripped_summary
                    )
                    model.summary = stripped_summary
            else:
                summary_return_context: OpenAIReturnContext | str | None = (
                    self.summarizer.test_summarize_code(
                        code_content,
                        model_id=model.id,
                        children_summaries=children_summaries,
                        dependency_summaries=dependency_summaries,
                        import_details=import_details,
                        parent_summary=parent_summary,
                        pass_number=pass_number,
                        # previous_summary=previous_summary,
                    )
                )
                if summary_return_context and isinstance(
                    summary_return_context, OpenAIReturnContext
                ):
                    if summary_return_context.summary:
                        self.graph_manager.update_vertex_summary_by_id(
                            model.id, summary_return_context.summary
                        )
                        model.summary = summary_return_context.summary
                    print(summary_return_context.summary)
                    self.prompt_tokens += summary_return_context.prompt_tokens
                    self.completion_tokens += summary_return_context.completion_tokens
                    logging.info(f"Total cost: ${self.total_cost:.2f}")

        return self.graph_manager.get_all_vertices() if self.graph_manager else None

    def _get_child_summaries(self, model: ModelType) -> str | None:
        """
        Gathers summaries of child models.

        Args:
            - `model` (ModelType): The model to gather child summaries for.

        Returns:
            - `str | None`: A string of concatenated child summaries or None if the model has no children.
        """
        child_summary_list: list[str] = []
        if model.children_ids:
            for child_id in model.children_ids:
                if child := self.graph_manager.get_vertex_model_by_id(child_id):
                    if child.summary:
                        child_summary_list.append(child.summary)
                    else:
                        # TODO: Add logic to gather all child summaries of a directory (modules and directories within the directory)
                        if not isinstance(child, DirectoryModel):
                            child_summary_list.append(
                                f"Child ({child_id}) code content:\n{child.code_content}\n"
                            )
        return (
            self._stringify_children_summaries(child_summary_list)
            if child_summary_list
            else None
        )

    def _stringify_children_summaries(self, children_summary_list: list[str]) -> str:
        """
        Converts all of the child summaries to a single string to be used in the prompt.

        Args:
            - `children_summary_list` (list[str]): A list of child summaries.

        Returns:
            - `str`: A string of all of the child summaries.
        """
        return "\n".join(children_summary_list)

    def _get_dependencies_summaries(self, model: ModelType) -> str | None:
        """
        Gathers summaries of dependencies and returns them as a string to be used in the prompt.

        Args:
            - `model` (ModelType): The model to gather dependency summaries for.

        Returns:
            - `str | None`: A string of dependency summaries or None if the model has no dependencies.
        """
        if isinstance(model, DirectoryModel):
            return None

        dependency_summary_list: list[str] = []

        if isinstance(model, ModuleModel):
            if model.imports:
                for _import in model.imports:
                    if import_summary := self._get_import_summary(_import):
                        dependency_summary_list.append(import_summary)
        elif model.dependencies:
            for dependency in model.dependencies:
                if isinstance(dependency, DependencyModel):
                    if dependency_summary := self._get_local_dependency_summary(
                        dependency, model
                    ):
                        dependency_summary_list.append(dependency_summary)
                elif isinstance(dependency, ImportModel):
                    if import_summary := self._get_import_summary(dependency):
                        dependency_summary_list.append(import_summary)

        return (
            self._stringify_dependencies_summaries(dependency_summary_list)
            if dependency_summary_list
            else None
        )

    def _get_local_dependency_summary(
        self,
        dependency: DependencyModel,
        model: ModelType,
    ) -> str | None:
        """
        Retrieves the summary of a local dependency to be used in the prompt.

        Args:
            - `dependency` (DependencyModel): The dependency to retrieve the summary for.
            - `model` (ModelType): The model to retrieve the summary for.

        Returns:
            - `str | None`: The summary of the local dependency or None if the dependency is not local.
        """
        if not model.children_ids:
            return None

        for child_id in model.children_ids:
            if child_id == dependency.code_block_id:
                if child := self.graph_manager.get_vertex_model_by_id(child_id):
                    if isinstance(child, DirectoryModel):
                        return None
                    return (
                        child.summary
                        if child.summary
                        else f"Dependency ({dependency.code_block_id}) code content:\n{child.code_content}\n"
                    )
        return None

    def _stringify_dependencies_summaries(
        self, dependencies_summary_list: list[str]
    ) -> str:
        """
        Converts all of the dependency summaries to a single string to be used in the prompt.

        Args:
            - `dependencies_summary_list` (list[str]): A list of dependency summaries.

        Returns:
            - `str`: A string of all of the dependency summaries.
        """
        return "\n".join(dependencies_summary_list)

    def _get_import_summary(self, import_model: ImportModel) -> str | None:
        """
        Retrieves the summary of an import to be used in the prompt.

        Args:
            - `import_model` (ImportModel): The import to retrieve the summary for.

        Returns:
            - `str | None`: The summary of the import or None if the import is not relevant.
        """
        if import_model.import_module_type == "LOCAL":
            if not import_model.import_names:
                return self._get_local_import_summary(import_model)
            else:
                return self._get_local_import_from_summary(import_model)
        else:
            return self._get_import_details(import_model)

    def _get_local_import_summary(self, dependency: ImportModel) -> str | None:
        """
        Retrieves the summary of a local import to be used in the prompt.

        Args:
            - `dependency` (ImportModel): The import to retrieve the summary for.

        Returns:
            - `str | None`: The summary of the local import or None if the import is not local.
        """
        if model := next(
            (m for m in self.all_models_tuple if m.id == dependency.local_module_id),
            None,
        ):
            if isinstance(model, DirectoryModel):
                return None
            return (
                model.summary
                if model.summary
                else f"Imported module ({dependency.local_module_id}) code content:\n{model.code_content}\n"
            )
        return None

    def _get_local_import_from_summary(self, dependency: ImportModel) -> str | None:
        """
        Retrieves the summary of a local import from to be used in the prompt.

        Args:
            - `dependency` (ImportModel): The import to retrieve the summary for.

        Returns:
            - `str | None`: The summary of the local import from or None if the import is not local.
        """
        for import_name in dependency.import_names:
            if model := next(
                (
                    m
                    for m in self.all_models_tuple
                    if m.id == import_name.local_block_id
                ),
                None,
            ):
                if isinstance(model, DirectoryModel):
                    return None
                return (
                    model.summary
                    if model.summary
                    else f"Imported code block ({dependency.local_module_id}) code content:\n{model.code_content}\n"
                )
        return None

    def _get_import_details(self, import_model: ImportModel) -> str | None:
        """
        Retrieves the details of an import to be used in the prompt.

        Args:
            - `import_model` (ImportModel): The import to retrieve the details for.

        Returns:
            - `str | None`: The details of the import or None if the import is not relevant.
        """
        if import_model.import_module_type == "LOCAL" or not import_model.import_names:
            return None

        import_names_list: list[str] = [
            f"{name.name} as {name.as_name}" if name.as_name else name.name
            for name in import_model.import_names
        ]

        if import_model.imported_from:
            return f"from {import_model.imported_from} import {', '.join(import_names_list)}"
        else:
            return f"import {', '.join(import_names_list)}"
