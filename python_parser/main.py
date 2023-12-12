import logging
from logging import Logger
from openai import OpenAI

from utilities.logger.logging_config import setup_logging
from visitor_manager.visitor_manager import VisitorManager

from ai_services.summarizer import OpenAISummarizer


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

    client = OpenAI()
    summarizer = OpenAISummarizer(client=client)

    visitor_manager = VisitorManager(summarizer, directory, output_directory)
    visitor_manager.process_files()
    visitor_manager.save_visited_directories()

    logger.info("Directory parsing completed.")


if __name__ == "__main__":
    setup_logging()
    main()
