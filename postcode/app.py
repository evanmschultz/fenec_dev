from postcode.updaters.graph_db_updater import GraphDBUpdater
from postcode.utilities.logger.logging_config import setup_logging

import postcode.types.chroma as chroma_types
from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)
from postcode.ai_services.librarians.chroma_librarians import ChromaLibrarian
from postcode.databases.chroma.chroma_setup import setup_chroma
from postcode.ai_services.chat.openai_agents import OpenAIChatAgent


# from postcode.updaters.standard_updater import StandardUpdater


def main(
    directory: str = ".",
    output_directory: str = "output_json",
) -> None:
    setup_logging()

    #   ==================== GraphDB ====================
    # graph_db_updater = GraphDBUpdater(directory, output_directory)
    # chroma_collection_manager: ChromaCollectionManager = graph_db_updater.update_all()
    chroma_collection_manager: ChromaCollectionManager = setup_chroma()
    chroma_librarian = ChromaLibrarian(chroma_collection_manager)
    openai_chat_agent = OpenAIChatAgent(chroma_librarian)
    print(openai_chat_agent.get_response("Which models are inherited by others?"))
    #   =================== End GraphDB ====================

    #   ==================== Standard ====================
    # chroma_context: ChromaSetupReturnContext = StandardUpdater.update_all(
    #     directory, output_directory, logger
    # )
    # StandardUpdater.update_all(directory, output_directory, logger)
    #   ==================  End Standard ====================
