import logging
from logging import Logger

from openai import OpenAI

from postcode.ai_services.summarization_manager import SummarizationManager
from postcode.json_management.json_handler import JSONHandler
from postcode.python_parser.models.models import ModuleModel

from postcode.utilities.logger.logging_config import setup_logging
from postcode.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)
from postcode.ai_services.summarizer import OpenAISummarizer


def main(
    directory: str = ".",
    output_directory: str = "output",
) -> None:
    """
    Parse the specified directory and save the results in the output directory.

    Args:
        directory (str): The path to the directory to parse.
        output_directory (str): The path to the output directory.

    Returns:
        None
    """

    logger: Logger = logging.getLogger(__name__)
    logger.info("Starting the directory parsing.")

    client = OpenAI(max_retries=4)
    summarizer = OpenAISummarizer(client=client)

    visitor_manager = VisitorManager(summarizer, directory, output_directory)
    process_files_return: VisitorManagerProcessFilesReturn = (
        visitor_manager.process_files()
    )

    module_models_tuple: tuple[ModuleModel, ...] = process_files_return.models_tuple
    directory_modules: dict[str, list[str]] = process_files_return.directory_modules
    summarization_manager = SummarizationManager(module_models_tuple, summarizer)
    summarization_manager.create_and_add_summaries_to_models()
    logger.info("Summarization complete")

    logger.info("Saving models as JSON")
    json_manager = JSONHandler(directory, directory_modules, output_directory)

    for module_model in module_models_tuple:
        json_manager.save_model_as_json(module_model, module_model.file_path)

    json_manager.save_visited_directories()
    logger.info("JSON save complete")

    logger.info("Directory parsing completed.")


if __name__ == "__main__":
    setup_logging()
    main()
