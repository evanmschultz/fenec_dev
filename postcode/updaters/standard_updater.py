# Create method, `update_all`, that updates the whole project, it parses all code, wipes all databases, and summarizes all code blocks,
# then updates all the databases with the new information.


from logging import Logger

from openai import OpenAI
from postcode.ai_services.summarizer.openai_summarizer import OpenAISummarizer
from postcode.ai_services.summarizer.standard_summarization_manager import (
    StandardSummarizationManager,
)

from postcode.databases.chroma.setup_chroma import (
    ChromaSetupReturnContext,
    setup_chroma,
)
from postcode.json_management.json_handler import JSONHandler

from postcode.models.models import ModuleModel
from postcode.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)


class StandardUpdater:
    @staticmethod
    def update_all(
        directory: str, output_directory: str, logger: Logger
    ) -> ChromaSetupReturnContext:
        visitor_manager = VisitorManager(directory, output_directory)
        process_files_return: VisitorManagerProcessFilesReturn = (
            visitor_manager.process_files()
        )

        module_models_tuple: tuple[ModuleModel, ...] = process_files_return.models_tuple
        client = OpenAI(max_retries=4)
        summarizer = OpenAISummarizer(client=client)
        summarization_manager = StandardSummarizationManager(
            module_models_tuple, summarizer
        )
        finalized_module_models: tuple[
            ModuleModel, ...
        ] = summarization_manager.create_summarizes_and_return_updated_models()

        logger.info("Summarization complete")

        logger.info("Saving models as JSON")
        directory_modules: dict[str, list[str]] = process_files_return.directory_modules
        json_manager = JSONHandler(directory, directory_modules, output_directory)

        for module_model in module_models_tuple:
            json_manager.save_model_as_json(module_model, module_model.file_path)

        json_manager.save_visited_directories()
        logger.info("JSON save complete")

        logger.info("Directory parsing completed.")

        chroma_context: ChromaSetupReturnContext = setup_chroma(
            finalized_module_models, logger
        )

        return chroma_context
