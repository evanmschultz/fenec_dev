# TODO: Add logic to gather all child summaries of a directory (modules and directories within the directory)

import logging
from rich import print

from postcode.ai_services.summarizer.summarization_context import (
    Summarizer,
    OpenAIReturnContext,
)
from postcode.ai_services.summarizer.summarization_mapper import SummarizationMapper
from postcode.databases.arangodb.arangodb_manager import ArangoDBManager

from postcode.types.postcode import ModelType

from postcode.models.models import (
    DependencyModel,
    DirectoryModel,
    ImportModel,
    ModuleModel,
)


class GraphDBSummarizationManager:
    """
    A class for managing summarization of models in a graph database.

    Args:
        - all_models_tuple (tuple[ModelType, ...]): Tuple of all models available for summarization.
        - summarization_mapper (SummarizationMapper): The SummarizationMapper instance for creating a summarization map.
        - summarizer (Summarizer): The Summarizer instance for generating code summaries.
        - graph_manager (ArangoDBManager): The ArangoDBManager instance for handling database interactions.

    Properties:
        - total_cost (float): Provides the total cost of the summarization process.

    Methods:
        - create_summaries_and_return_updated_models(): Creates summaries and updates models in the graph database.

    Example:
        ```python
        # Instantiate GraphDBSummarizationManager
        summarization_manager = GraphDBSummarizationManager(
            all_models_tuple=(ModuleModel(id="module_1"), FunctionModel(id="function_1")),
            summarization_mapper=my_summarization_mapper_instance,
            summarizer=my_summarizer_instance,
            graph_manager=my_arangodb_manager_instance
        )

        # Create summaries and update models
        updated_models = summarization_manager.create_summaries_and_return_updated_models()
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
        prompt_cost: int = self.prompt_tokens * 1  # Costs 1 cent per 1,000 tokens
        completion_cost: int = (
            self.completion_tokens * 3
        )  # Costs 3 cents per 1,000 tokens
        return (prompt_cost + completion_cost) / 100_000  # Convert to dollars

    def create_summaries_and_return_updated_models(self) -> list[ModelType] | None:
        """
        Creates summaries and updates models in the graph database.

        Returns:
            - list[ModelType] | None: Updated models in the graph database or None if graph_manager is not provided.
        """
        summarization_map: list[
            ModelType
        ] = self.summarization_mapper.create_summarization_map()
        models_to_summarize_count: int = len(summarization_map)
        models_summarized_count: int = 0

        for model in summarization_map:
            children_summaries: str | None = None
            dependency_summaries: str | None = None
            import_details: str | None = None

            if model.children_ids:
                if children_summary_list := self._get_child_summaries(model):
                    self._get_child_summaries(model)

                    children_summaries: str | None = self._stringify_children_summaries(
                        children_summary_list
                    )

            # if isinstance(model, DirectoryModel):
            #     ...

            elif isinstance(model, ModuleModel):
                if model.imports:
                    dependency_summaries = self._get_dependencies_summaries(model)
                    import_details = ""
                    for _import in model.imports:
                        if import_summary := self._get_import_details(_import):
                            import_details += f"\n{import_summary}"
            else:
                if not isinstance(model, DirectoryModel):
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

            code_content: str = ""
            if isinstance(model, DirectoryModel):
                code_content = ""
            else:
                code_content = model.code_content

            summary_return_context: OpenAIReturnContext | None = (
                self.summarizer.summarize_code(
                    code_content,
                    model_id=model.id,
                    children_summaries=children_summaries,
                    dependency_summaries=dependency_summaries,
                    import_details=import_details,
                )
            )
            if summary_return_context:
                if summary_return_context.summary:
                    self.graph_manager.update_vertex_summary_by_id(
                        model.id, summary_return_context.summary
                    )
                print(summary_return_context.summary)
                self.prompt_tokens += summary_return_context.prompt_tokens
                self.completion_tokens += summary_return_context.completion_tokens
                logging.info(f"Total cost: ${self.total_cost:.2f}")

        logging.debug(f"Summarization map length: {len(summarization_map)}")
        # pprint([model.id for model in summarization_map][::-1])
        count = 1
        for model in summarization_map[::-1]:
            # pprint({"count": count, "id": model.id})
            count += 1
        return self.graph_manager.get_all_vertices() if self.graph_manager else None

    def _get_child_summaries(self, model: ModelType) -> list[str] | None:
        """
        Gathers summaries of child models.

        Args:
            - model (ModelType): The model to gather child summaries for.

        Returns:
            - list[str] | None: A list of child summaries or None if the model has no children.
        """

        child_summary_list: list[str] = []
        if model.children_ids:
            for child_id in model.children_ids:
                if child := self.graph_manager.get_vertex_model_by_id(child_id):
                    if child.summary:
                        child_summary: str = child.summary

                    else:
                        # TODO: Add logic to gather all child summaries of a directory (modules and directories within the directory)
                        if isinstance(child, DirectoryModel):
                            # for child_child_id in child.children_ids:
                            #     if child_child := self.graph_manager.get_vertex_model_by_id(
                            #         child_child_id
                            #     ):
                            #         if child_child.summary:
                            #             child_summary = child_child.summary
                            #             break
                            continue

                        child_summary = (
                            f"Child ({child_id}) code content:\n{child.code_content}\n"
                        )
                    child_summary_list.append(child_summary)
        return child_summary_list

    def _stringify_children_summaries(self, children_summary_list: list[str]) -> str:
        """
        Converts all of the child summaries to a single string to be used in the prompt.

        Args:
            - children_summary_list (list[str]): A list of child summaries.

        Returns:
            - str: A string of all of the child summaries.
        """

        children_summaries: str = ""
        for child_summary in children_summary_list:
            children_summaries += f"\n{child_summary}"
        return children_summaries

    def _get_dependencies_summaries(self, model: ModelType) -> str | None:
        """
        Gathers summaries of dependencies and returns them as a string to be used in the prompt.

        Args:
            - model (ModelType): The model to gather dependency summaries for.

        Returns:
            - str | None: A string of dependency summaries or None if the model has no dependencies.
        """

        dependency_list: list[ImportModel | DependencyModel] | list[ImportModel] = []
        dependency_summary_list: list[str] = []

        if isinstance(model, DirectoryModel):
            return None

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

        dependency_summaries: str | None = self._stringify_dependencies_summaries(
            dependency_summary_list
        )

        return dependency_summaries

    def _get_local_dependency_summary(
        self,
        dependency: DependencyModel,
        model: ModelType,
    ) -> str | None:
        """
        Retrieves the summary of a local dependency to be used in the prompt.

        Args:
            - dependency (DependencyModel): The dependency to retrieve the summary for.
            - model (ModelType): The model to retrieve the summary for.

        Returns:
            - str | None: The summary of the local dependency or None if the dependency is not local.
        """
        if not model.children_ids:
            return None

        for child_id in model.children_ids:
            if child_id == dependency.code_block_id:
                for model in self.all_models_tuple:
                    if model.id == child_id:
                        if isinstance(model, DirectoryModel):
                            return None

                        if model.summary:
                            return model.summary
                        else:
                            return f"Dependency ({dependency.code_block_id}) code content:\n{model.code_content}\n"
        return None

    def _stringify_dependencies_summaries(
        self, dependencies_summary_list: list[str] | None
    ) -> str | None:
        """
        Converts all of the dependency summaries to a single string to be used in the prompt.

        Args:
            - dependencies_summary_list (list[str] | None): A list of dependency summaries.

        Returns:
            - str | None: A string of all of the dependency summaries or None if the list is empty.
        """
        if not dependencies_summary_list:
            return None

        dependency_summaries: str = ""
        for dependency_summary in dependencies_summary_list:
            dependency_summaries += f"\n{dependency_summary}"
        return dependency_summaries

    def _get_local_import_summary(self, dependency: ImportModel) -> str | None:
        """
        Retrieves the summary of a local import to be used in the prompt.

        Args:
            - dependency (ImportModel): The import to retrieve the summary for.

        Returns:
            - str | None: The summary of the local import or None if the import is not local.
        """

        for model in self.all_models_tuple:
            if model.id == dependency.local_module_id:
                import_summary: str | None = None
                if model.summary:
                    import_summary = model.summary
                else:
                    if not isinstance(model, DirectoryModel):
                        import_summary = f"Imported module ({dependency.local_module_id}) code content:\n{model.code_content}\n"

                return import_summary
        return None

    def _get_local_import_from_summary(self, dependency: ImportModel) -> str | None:
        """
        Retrieves the summary of a local import from to be used in the prompt.

        Args:
            - dependency (ImportModel): The import to retrieve the summary for.

        Returns:
            - str | None: The summary of the local import from or None if the import is not local.
        """

        for import_name in dependency.import_names:
            for model in self.all_models_tuple:
                if model.id == import_name.local_block_id:
                    if isinstance(model, DirectoryModel):
                        return None

                    import_summary: str = ""
                    if model.summary:
                        import_summary = model.summary
                    else:
                        import_summary = f"Imported code block ({dependency.local_module_id}) code content:\n{model.code_content}\n"
                    return import_summary
        return None

    def _get_import_details(self, import_model: ImportModel) -> str | None:
        """
        Returns the import details to be used in the prompt.

        Args:
            - import_model (ImportModel): The import to retrieve the details for.

        Returns:
            - str | None: The import details or None if the import is local.
        """

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
