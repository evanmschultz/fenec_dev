from postcode.updaters.graph_db_updater import GraphDBUpdater
from postcode.utilities.logger.logging_config import setup_logging

from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)
from postcode.ai_services.librarians.chroma_librarians import ChromaLibrarian
from postcode.ai_services.chat.openai_agents import OpenAIChatAgent

from rich.console import Console
from rich.prompt import Prompt


# from postcode.updaters.standard_updater import StandardUpdater


def update_all_with_graph_db(
    directory: str = ".", output_directory: str = "output_json"
) -> ChromaCollectionManager:
    """
    Parses and summarizes all code snippets in the specified directory and updates the graph database and sets up a
    ChromaDB collection.

    Args:
        - directory (str, optional): The directory containing code snippets to parse and summarize. Defaults to ".".
        - output_directory (str, optional): The directory to output the parsed and summarized code snippets.
            Defaults to "output_json".

    Returns:
        - ChromaCollectionManager: An instance of ChromaCollectionManager for the specified collection.
    """
    setup_logging()

    graph_db_updater = GraphDBUpdater(directory, output_directory)
    return graph_db_updater.update_all()


def _cli_loop(openai_chat_agent: OpenAIChatAgent, console: Console) -> None:
    """
    Sets up a simple CLI loop for the chat agent.

    Args:
        - openai_chat_agent (OpenAIChatAgent): The OpenAI chat agent.
        - console (Console): The Rich Console instance.
    """
    while True:
        user_input: str = Prompt.ask(
            "[bold blue]Ask a question about Postcode or type 'exit' to end[/]"
        )
        if user_input.lower() == "exit":
            break
        response: str | None = openai_chat_agent.get_response(user_input)
        console.print(f"[bold green]Response:[/bold green]\n{response}")


def simple_chat(chroma_collection_manager: ChromaCollectionManager) -> None:
    """
    Creates a simple chat app in the terminal using the OpenAI chat agent.

    Args:
        - chroma_collection_manager (ChromaCollectionManager): The Chroma collection manager instance.

    Examples:
        ```Python
        from postcode import simple_chat
        from postcode import setup_chroma

        chroma_collection_manager = setup_chroma()
        simple_chat(chroma_collection_manager)
        # Now you can ask questions about Postcode in the terminal!
        ```
    """

    setup_logging()
    console = Console()
    chroma_librarian = ChromaLibrarian(chroma_collection_manager)
    openai_chat_agent = OpenAIChatAgent(chroma_librarian)

    try:
        _cli_loop(openai_chat_agent, console)
    finally:
        console.print("Exiting the simple chat app.")
