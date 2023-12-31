from logging import Logger
from typing import Union

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
    ClassModel,
    DirectoryModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)
from postcode.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)
from postcode.types.postcode import ModelType


# ModelType = Union[
#     ModuleModel,
#     ClassModel,
#     FunctionModel,
#     StandaloneCodeBlockModel,
#     DirectoryModel,
# ]


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

        self.arango_connector.delete_all_collections()
        self.arango_connector.ensure_collections()
        self.graph_manager = ArangoDBManager(arango_connector)

    def update_all(
        self,
        directory: str,
        output_directory: str,
        logger: Logger,
    ) -> ChromaSetupReturnContext:
        logger.info("Starting the directory parsing.")

        visitor_manager = VisitorManager(directory, output_directory)
        process_files_return: VisitorManagerProcessFilesReturn = (
            visitor_manager.process_files()
        )

        models_tuple: tuple[ModelType, ...] = process_files_return.models_tuple
        module_ids: list[str] = [
            model.id for model in models_tuple if isinstance(model, ModuleModel)
        ]

        directory_modules: dict[str, list[str]] = process_files_return.directory_modules
        self.graph_manager.upsert_models(
            list(models_tuple)
        ).process_imports_and_dependencies().get_or_create_graph()
        summarization_mapper = SummarizationMapper(
            module_ids, models_tuple, self.graph_manager
        )
        client = OpenAI(max_retries=4)
        summarizer = OpenAISummarizer(client=client)
        summarization_manager = GraphDBSummarizationManager(
            models_tuple, summarization_mapper, summarizer, self.graph_manager
        )
        finalized_module_models: list[
            ModuleModel
        ] | None = summarization_manager.create_summaries_and_return_updated_models()
        logger.info("Summarization complete")

        logger.info("Saving models as JSON")
        # json_manager = JSONHandler(directory, directory_modules, output_directory)

        # for module_model in module_models_tuple:
        #     json_manager.save_model_as_json(module_model, module_model.file_path)

        # json_manager.save_visited_directories()
        # logger.info("JSON save complete")

        directory_modules: dict[str, list[str]] = process_files_return.directory_modules
        json_manager = JSONHandler(directory, directory_modules, output_directory)

        for model in models_tuple:
            if isinstance(model, DirectoryModel):
                output_path: str = model.id

            else:
                output_path: str = model.file_path + model.id
            json_manager.save_model_as_json(model, output_path)

        json_manager.save_visited_directories()
        logger.info("JSON save complete")

        logger.info("Directory parsing completed.")

        logger.info("Directory parsing completed.")

        # self.graph_manager.upsert_models(
        #     list(finalized_module_models)
        # ).process_imports_and_dependencies().get_or_create_graph()

        if finalized_module_models:
            chroma_context: ChromaSetupReturnContext = setup_chroma(
                finalized_module_models, logger
            )
        else:
            raise Exception("No finalized models returned from summarization.")

        return chroma_context
