from pathlib import Path
from fenec.ai_services.summarizer.summarizer_protocol import Summarizer
from fenec.updaters.graph_db_updater import GraphDBUpdater
from fenec.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)
from fenec.utilities.configs.configs import (
    OpenAIChatConfigs,
    ChatConfigs,
    OllamaChatConfigs,
    OpenAISummarizationConfigs,
    OllamaSummarizationConfigs,
)
from fenec.ai_services.summarizer.summarizer_factory import create_summarizer
from fenec.ai_services.chat.openai_agents import OpenAIChatAgent
from fenec.ai_services.librarians.chroma_librarians import ChromaLibrarian
from fenec.databases.chroma.chroma_setup import setup_chroma
from fenec.utilities.logger.logging_config import setup_logging


class Fenec:
    """
    Main interface for the Fenec package.

    This class provides methods to process a codebase and interact with it through a chat interface.

    Attributes:
        - `updater` (GraphDBUpdater): The updater for the graph database.
            - default: GraphDBUpdater()

    Methods:
        - `process_entire_codebase`(updater: GraphDBUpdater = GraphDBUpdater()): Process the entire codebase using the GraphDBUpdater.
        - `chat`(message: str, chat_config: ChatCompletionConfigs = ChatCompletionConfigs()): Interact with the processed codebase through a chat interface

    Example:
        ```python
        summarizer = OpenAISummarizer()
        updater = GraphDBUpdater("/path/to/project", summarizer=summarizer, output_directory="output_json")
        fenec = Fenec("/path/to/project", output_directory="output_json")

        fenec.process_entire_codebase(summarizer)
        response = fenec.chat("What does the main function do?")
        print(response)
        ```
    """

    def __init__(
        self,
        path: Path = Path("."),
        summarization_configs: (
            OpenAISummarizationConfigs | OllamaSummarizationConfigs
        ) = OpenAISummarizationConfigs(),
        chat_configs: OpenAIChatConfigs = OpenAIChatConfigs(),
    ) -> None:
        self.path: Path = path
        self.summarization_configs: (
            OpenAISummarizationConfigs | OllamaSummarizationConfigs
        ) = summarization_configs
        self.chat_configs: OpenAIChatConfigs = chat_configs
        self.updater: GraphDBUpdater = GraphDBUpdater(
            summarization_configs=self.summarization_configs
        )
        setup_logging()

    def process_codebase(
        self,
        num_of_passes: int = 1,
        process_all: bool = False,
    ) -> None:
        """
        Process the entire codebase using the GraphDBUpdater.

        This method initializes the GraphDBUpdater, processes the codebase, and stores the resulting
        ChromaCollectionManager for later use in chat interactions.

        Args:
            - `updater` (GraphDBUpdater): The updater for the graph database.

        Raises:
            - `Exception`: If there's an error during the codebase processing.
        """

        try:
            if process_all:
                self.chroma_collection_manager: ChromaCollectionManager = (
                    self.updater.update_all(num_of_passes)
                )
            else:
                self.chroma_collection_manager: ChromaCollectionManager = (
                    self.updater.update_changed(num_of_passes)
                )
            self.chroma_librarian = ChromaLibrarian(self.chroma_collection_manager)
        except Exception as e:
            raise Exception(f"Error processing codebase: {str(e)}")

    def connect_to_vectorstore(self, chromadb_name: str = "fenec") -> None:
        """
        Connect to an existing ChromaDB collection.

        This method initializes the ChromaCollectionManager for the specified collection name
        and stores it for later use in chat interactions.

        Args:
            - `chromadb_name` (str): Name of the ChromaDB collection.

        Raises:
            - `Exception`: If there's an error during the connection.
        """

        try:
            self.chroma_collection_manager: ChromaCollectionManager = setup_chroma(
                chromadb_name
            )
            self.chroma_librarian = ChromaLibrarian(self.chroma_collection_manager)
        except Exception as e:
            raise Exception(f"Error connecting to ChromaDB: {str(e)}")

    def chat(
        self,
        message: str,
    ) -> str:
        """
        Interact with the processed codebase through a chat interface.

        This method uses the stored ChromaCollectionManager to process the user's message
        and return a response.

        Args:
            - `message` (str): The user's input message or question.
            - `chat_config` (ChatCompletionConfigs): Configuration for the chat completion.
                - default: ChatCompletionConfigs().

        Returns:
            - `str`: The AI's response to the user's message.

        Raises:
            - `ValueError`: If the codebase hasn't been processed yet.
        """
        if not self.chroma_librarian:
            raise ValueError(
                "Codebase has not been processed. Call process_codebase() first."
            )
        openai_chat_agent = OpenAIChatAgent(
            self.chroma_librarian, configs=self.chat_configs
        )
        response: str | None = openai_chat_agent.get_response(message)
        return response if response else "I'm sorry, I couldn't generate a response."
