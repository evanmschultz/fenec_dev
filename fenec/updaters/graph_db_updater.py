import json
import logging
import os

from fenec.ai_services.summarizer.graph_db_summarization_manager import (
    GraphDBSummarizationManager,
)
from fenec.ai_services.summarizer.openai_summarizer import OpenAISummarizer
from fenec.ai_services.summarizer.ollama_summarizer import OllamaSummarizer
from fenec.ai_services.summarizer.summarization_mapper import SummarizationMapper
import fenec.ai_services.summarizer.summarizer_factory as summarizer_factory
from fenec.ai_services.summarizer.summarizer_protocol import Summarizer
from fenec.databases.arangodb.arangodb_connector import ArangoDBConnector

from fenec.databases.arangodb.arangodb_manager import ArangoDBManager
from fenec.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)
import fenec.databases.chroma.chroma_setup as chroma_setup
from fenec.json_management.json_handler import JSONHandler
from fenec.models.models import (
    DirectoryModel,
    ModuleModel,
)
from fenec.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)
from fenec.types.fenec import ModelType
from fenec.updaters.change_detector import ChangeDetector
import fenec.updaters.git_updater as git_updater
from fenec.utilities.configs.configs import (
    OllamaSummarizationConfigs,
    OpenAISummarizationConfigs,
)


class GraphDBUpdater:
    """
    Graph DB based updater supporting multi-pass summarization.

    Updates, parses the files in a directory, saves the models as JSON, in the graph database, and in a ChromaDB collection.

    Args:
        - `directory` (str) - The directory of the project to update.
            default - "."
        - `summarization_configs` (OpenAISummarizationConfigs | OllamaSummarizationConfigs) - The configs for the summarizer that will
            be used to create the summarizer and set its configurations.
        - `output_directory` (str) - The directory to save the JSON files.
            - default - "pc_output_json"
        - `graph_connector` (ArangoDBConnector) - The ArangoDB connector to use for connecting to the graph database.
            - default - ArangoDBConnector() - instantiates a new ArangoDBConnector with its default values

    Example:
        ```Python
        from fenec.databases.arangodb.arangodb_connector import ArangoDBConnector
        from fenec.updaters.graph_db_updater import GraphDBUpdater

        # Create the ArangoDB connector.
        arango_connector = ArangoDBConnector()

        # Create the GraphDBUpdater.
        graph_updater = GraphDBUpdater(directory, output_directory, arango_connector)

        # Update all the models for the project and setup Chroma.
        chroma_collection_manager = graph_updater.update_all()
        ```
    """

    def __init__(
        self,
        directory: str = ".",
        *,
        summarization_configs: (
            OpenAISummarizationConfigs | OllamaSummarizationConfigs
        ) = OllamaSummarizationConfigs(),
        output_directory: str = "pc_output_json",
        graph_connector: ArangoDBConnector = ArangoDBConnector(),
    ) -> None:
        self.directory: str = directory
        self.summarization_configs: (
            OpenAISummarizationConfigs | OllamaSummarizationConfigs
        ) = summarization_configs
        self.summarizer: Summarizer = summarizer_factory.create_summarizer(
            summarization_configs
        )
        self.output_directory: str = output_directory
        self.graph_connector: ArangoDBConnector = graph_connector

        self.graph_manager = ArangoDBManager(graph_connector)
        self.last_commit_file = os.path.join(self.output_directory, "last_commit.json")

    def update_changed(self, num_passes: int = 1) -> ChromaCollectionManager:
        """
        Updates only the changed files and their connected code blocks since the last update.

        Args:
            last_commit_hash (str): The commit hash of the last update.
            num_passes (int): Number of summarization passes to perform. Must be either 1 or 3. Default is 1.

        Returns:
            ChromaCollectionManager: The updated ChromaDB collection manager.
        """
        if num_passes not in [1, 3]:
            raise ValueError("Number of passes must be either 1 or 3")

        last_commit_hash: str = self._get_last_commit_hash()
        changed_files: list[str] = git_updater.get_changed_files_since_last_update(
            last_commit_hash
        )

        # Parse all files (we need the full structure to detect connections)
        process_files_return = self._visit_and_parse_files(self.directory)
        all_models = process_files_return.models_tuple

        # Detect affected models
        change_detector = ChangeDetector(
            all_models,
            self.graph_manager,
        )
        affected_model_ids: set[str] = change_detector.get_affected_models(
            changed_files, both_directions=True if num_passes == 3 else False
        )

        # Filter models to only affected ones
        affected_models = [
            model for model in all_models if model.id in affected_model_ids
        ]
        affected_models = tuple(affected_models)

        # Update graph DB with all models (to ensure structure is up-to-date)
        self._upsert_models_to_graph_db(all_models)

        # Summarize and update only affected models
        finalized_models = self._map_and_summarize_models(affected_models, num_passes)

        if not finalized_models:
            raise Exception("No finalized models returned from summarization.")

        # Update databases with finalized models
        self._upsert_models_to_graph_db(tuple(finalized_models))
        chroma_manager = chroma_setup.setup_chroma_with_update(finalized_models)

        current_commit_hash = git_updater.get_current_commit_hash()
        self._save_last_commit_hash(current_commit_hash)

        return chroma_manager

    def _save_last_commit_hash(self, commit_hash: str) -> None:
        """
        Saves the last commit hash to a file.

        Args:
            commit_hash (str): The commit hash to save.
        """
        os.makedirs(os.path.dirname(self.last_commit_file), exist_ok=True)
        with open(self.last_commit_file, "w") as f:
            json.dump({"last_commit": commit_hash}, f)

    def _get_last_commit_hash(self) -> str:
        """
        Retrieves the last commit hash from the file.

        Returns:
            str: The last commit hash, or an empty string if the file doesn't exist.
        """
        if not os.path.exists(self.last_commit_file):
            return ""
        with open(self.last_commit_file, "r") as f:
            data = json.load(f)
            return data.get("last_commit", "")

    def update_all(self, num_passes: int = 1) -> ChromaCollectionManager:
        """
        Updates all the models for a project using the graph database with multi-pass summarization support.

        Args:
            - num_passes (int): Number of summarization passes to perform. Must be either 1 or 3. Default is 1.

        Note:
            This method will delete all the existing collections in the graph database, summarize every code block in the project,
            and save the new models in the graph database and as JSON. Use with caution as it is expensive with respect to time, resources,
            and money.

        Returns:
            - `chroma_collection_manager` (ChromaDBCollectionManager): The ChromaDB collection manager.

        Raises:
            - `Exception`: If no finalized models are returned from summarization.
            - `ValueError`: If num_passes is not 1 or 3.

        Example:
            ```Python
            graph_updater = GraphDBUpdater(directory, output_directory)

            # Update all the models for the project with multi-pass summarization and setup Chroma.
            chroma_manager = graph_updater.update_all(num_passes=3)
            ```
        """
        if num_passes not in [1, 3]:
            raise ValueError("Number of passes must be either 1 or 3")

        self.graph_connector.delete_all_collections()
        self.graph_connector.ensure_collections()

        process_files_return: VisitorManagerProcessFilesReturn = (
            self._visit_and_parse_files(self.directory)
        )
        models_tuple: tuple[ModelType, ...] = process_files_return.models_tuple

        self._upsert_models_to_graph_db(models_tuple)

        finalized_models: list[ModelType] | None = self._map_and_summarize_models(
            models_tuple, num_passes
        )

        if not finalized_models:
            raise Exception("No finalized models returned from summarization.")

        json_manager = JSONHandler(
            self.directory,
            process_files_return.directory_modules,
            self.output_directory,
        )
        self._save_json(finalized_models, json_manager)
        self._upsert_models_to_graph_db(tuple(finalized_models))

        current_commit_hash: str = git_updater.get_current_commit_hash()
        self._save_last_commit_hash(current_commit_hash)

        return chroma_setup.setup_chroma_with_update(finalized_models)

    def _visit_and_parse_files(
        self, directory: str
    ) -> VisitorManagerProcessFilesReturn:
        """Visits and parses the files in the directory."""

        logging.info("Starting the directory parsing.")
        visitor_manager = VisitorManager(directory)

        return visitor_manager.process_files()

    def _get_module_ids(self, models_tuple: tuple[ModelType, ...]) -> list[str]:
        """Returns a list of module IDs from the models tuple."""

        return [model.id for model in models_tuple if isinstance(model, ModuleModel)]

    def _upsert_models_to_graph_db(self, models_tuple: tuple[ModelType, ...]) -> None:
        """Upserts the models to the graph database."""

        self.graph_manager.upsert_models(
            list(models_tuple)
        ).process_imports_and_dependencies().get_or_create_graph()

    def _save_json(self, models: list[ModelType], json_manager: JSONHandler) -> None:
        """Saves the models as JSON."""

        logging.info("Saving models as JSON")
        for model in models:
            if isinstance(model, DirectoryModel):
                output_path: str = model.id

            else:
                output_path: str = model.file_path + model.id
            json_manager.save_model_as_json(model, output_path)

        json_manager.save_visited_directories()
        logging.info("JSON save complete")

    def _map_and_summarize_models(
        self,
        models_tuple: tuple[ModelType, ...],
        num_passes: int,
    ) -> list[ModelType] | None:
        """Maps and summarizes the models using multi-pass summarization."""

        module_ids: list[str] = self._get_module_ids(models_tuple)
        summarization_mapper = SummarizationMapper(
            module_ids, models_tuple, self.graph_manager
        )
        summarization_manager = GraphDBSummarizationManager(
            models_tuple, summarization_mapper, self.summarizer, self.graph_manager
        )

        finalized_models: list[ModelType] | None = (
            summarization_manager.create_summaries_and_return_updated_models(num_passes)
        )
        logging.info(f"Multi-pass summarization complete (passes: {num_passes})")

        return finalized_models if finalized_models else None
