from typing import Union
from chromadb import EphemeralClient, PersistentClient, HttpClient

# import postcode.types.chroma as chroma_types
from chromadb.config import DEFAULT_DATABASE, DEFAULT_TENANT, Settings
from chromadb.api import ClientAPI
from chromadb.api.types import (
    DataLoader,
    CollectionMetadata,
    GetResult,
    QueryResult,
    Where,
    WhereDocument,
    Include,
    URIs,
    Loadable,
    Metadata,
    Embedding,
)
from chromadb import Collection
from chromadb import EmbeddingFunction




class ChromaDBClientBuilder:
    """
    This class is used to create a ChromaDB client. It provides three methods for creating a ChromaDB client:

    Methods:
        - `create_ephemeral_client`: Creates an ephemeral client. This means the client will be in memory and will not
            persist to disk. This is useful for testing and development.
        - `create_persistent_client`: Creates a persistent client. This means the client will persist to disk, but will still
            run in memory. This is useful for testing and development.
        - `create_http_client`: Creates an HTTP client. This means the client will connect to a remote ChromaDB instance. The
            default host is localhost and the default port is 8087 for local development, and is the only method suggested for
            production in the ChromaDB documentation.

    Notes:
        - Import defined in postcode.databases.chroma `__init__.py` so import from postcode.databases.chroma:
            `from postcode.databases.chroma import ChromaDBClientBuilder`

    Examples:
        ```Python
        from postcode.databases.chroma import ChromaDBClientBuilder
        import postcode.types.chromadb.types as chroma_types

        client: chroma_types.ClientAPI = ChromaDBClientBuilder.create_persistent_client()
        ```
    """

    @staticmethod
    def create_ephemeral_client(
        settings: Settings | None = None,
        tenant: str = DEFAULT_TENANT,
        database: str = DEFAULT_DATABASE,
    ) -> ClientAPI:
        """
        Creates an in-memory instance of Chroma. This is useful for testing and development, but not recommended for production use according to
        the ChromaDB documentation.

        Args:
            - settings (chroma_types.Settings): The settings to use for the ephemeral client.
            - tenant (str): The tenant to use for the ephemeral client.
            - database (str): The database to use for the ephemeral client.
        """
        return EphemeralClient(
            settings=settings if settings else Settings(),
            tenant=tenant,
            database=database,
        )

    @staticmethod
    def create_persistent_client(
        path: str = "./chroma",
        settings: Settings | None = None,
        tenant: str = DEFAULT_TENANT,
        database: str = DEFAULT_DATABASE,
    ) -> ClientAPI:
        """
        Creates a persistent instance of Chroma that saves to disk. This is useful for testing and development, but not recommended for production use
        according to the ChromaDB documentation.

        Args:
            - path (str): The path to the ChromaDB directory.
            - settings (chroma.Settings): The settings to use for the persistent client.
            - tenant (str): The tenant to use for the persistent client.
            - database (str): The database to use for the persistent client.
        """
        return PersistentClient(
            path=path,
            settings=settings if settings else Settings(),
            tenant=tenant,
            database=database,
        )

    @staticmethod
    def create_http_client(
        host: str = "localhost",
        port: str = "8087",
        ssl: bool = False,
        headers: dict[str, str] = {},
        settings: Settings | None = None,
        tenant: str = DEFAULT_TENANT,
        database: str = DEFAULT_DATABASE,
    ) -> ClientAPI:
        """
        Creates a client that connects to a remote Chroma server. This supports many clients connecting to the same server, and is the
        recommended way to use Chroma in production according to the ChromaDB Documentation.

        Args:
            - host (str): The host of the ChromaDB server.
            - port (str): The port of the ChromaDB server.
            - ssl (bool): Whether or not to use SSL.
            - headers (dict[str, str]): The headers to use for the HTTP client.
            - settings (chroma_types.Settings): The settings to use for the HTTP client.
            - tenant (str): The tenant to use for the HTTP client.
            - database (str): The database to use for the HTTP client.
        """
        return HttpClient(
            host=host,
            port=port,
            ssl=ssl,
            headers=headers,
            settings=settings if settings else Settings(),
            tenant=tenant,
            database=database,
        )
