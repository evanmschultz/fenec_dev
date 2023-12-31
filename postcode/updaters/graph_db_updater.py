from logging import Logger

from openai import OpenAI
from postcode.ai_services.summarizer.graph_db_summarization_manager import (
    GraphDBSummarizationManager,
)
from postcode.ai_services.summarizer.openai_summarizer import OpenAISummarizer
from postcode.ai_services.summarizer.summarization_mapper import SummarizationMapper
from postcode.databases.arangodb.arangodb_connector import ArangoDBConnector

from postcode.databases.arangodb.arangodb_manager import ArangoDBManager
from postcode.databases.chroma.setup_chroma import (
    ChromaSetupReturnContext,
    setup_chroma,
)
from postcode.json_management.json_handler import JSONHandler
from postcode.models.models import (
    DirectoryModel,
    ModuleModel,
)
from postcode.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)
from postcode.types.postcode import ModelType


class GraphDBUpdater:
    def __init__(
        self,
        directory: str,
        output_directory: str,
        logger: Logger,
        arango_connector: ArangoDBConnector = ArangoDBConnector(),
    ) -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self.logger: Logger = logger
        self.arango_connector: ArangoDBConnector = arango_connector

        self.graph_manager = ArangoDBManager(arango_connector)

    def update_all(
        self,
        directory: str,
        output_directory: str,
        logger: Logger,
    ) -> ChromaSetupReturnContext:
        self.arango_connector.delete_all_collections()
        self.arango_connector.ensure_collections()

        process_files_return: VisitorManagerProcessFilesReturn = (
            self._visit_and_parse_files(directory, logger)
        )
        models_tuple: tuple[ModelType, ...] = process_files_return.models_tuple

        self._upsert_models_to_graph_db(models_tuple)

        finalized_models: list[ModelType] | None = self._map_and_summarize_models(
            models_tuple, logger
        )

        if not finalized_models:
            raise Exception("No finalized models returned from summarization.")

        json_manager = JSONHandler(
            directory, process_files_return.directory_modules, output_directory
        )
        self._save_json(finalized_models, json_manager, logger)
        self._upsert_models_to_graph_db(tuple(finalized_models))

        return setup_chroma(finalized_models, logger)

    def _visit_and_parse_files(
        self, directory: str, logger: Logger
    ) -> VisitorManagerProcessFilesReturn:
        """Visits and parses the files in the directory."""

        logger.info("Starting the directory parsing.")
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

    def _save_json(
        self, models: list[ModelType], json_manager: JSONHandler, logger: Logger
    ) -> None:
        """Saves the models as JSON."""

        logger.info("Saving models as JSON")
        for model in models:
            if isinstance(model, DirectoryModel):
                output_path: str = model.id

            else:
                output_path: str = model.file_path + model.id
            json_manager.save_model_as_json(model, output_path)

        json_manager.save_visited_directories()
        logger.info("JSON save complete")

    def _map_and_summarize_models(
        self,
        models_tuple: tuple[ModelType, ...],
        logger: Logger,
    ) -> list[ModelType] | None:
        """Maps and summarizes the models."""

        module_ids: list[str] = self._get_module_ids(models_tuple)
        summarization_mapper = SummarizationMapper(
            module_ids, models_tuple, self.graph_manager
        )
        client = OpenAI(max_retries=4)
        summarizer = OpenAISummarizer(client=client)
        summarization_manager = GraphDBSummarizationManager(
            models_tuple, summarization_mapper, summarizer, self.graph_manager
        )

        finalized_models: list[
            ModelType
        ] | None = summarization_manager.create_summaries_and_return_updated_models()
        logger.info("Summarization complete")

        return finalized_models if finalized_models else None
