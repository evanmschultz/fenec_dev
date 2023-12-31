from dataclasses import dataclass
from logging import Logger

import chromadb
from postcode.databases.chroma.chromadb_client_manager import ChromaDBClientManager

from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaDBCollectionManager,
)

import postcode.types.chroma as chroma_types

# from chromadb.config import DEFAULT_DATABASE, DEFAULT_TENANT, Settings
# from chromadb.api import ClientAPI
# from chromadb.api.types import (
#     DataLoader,
#     CollectionMetadata,
#     GetResult,
#     QueryResult,
#     Where,
#     WhereDocument,
#     Include,
#     URIs,
#     Loadable,
#     Metadata,
#     Embedding,
# )
# from chromadb import Collection
# from chromadb import EmbeddingFunction

# from postcode.models.models import ModuleModel
from postcode.types.postcode import ModelType


@dataclass
class ChromaSetupReturnContext:
    """
    Represents the return value of the ChromaDB setup method.

    Attributes:
        - chroma_collection_manager (ChromaDBCollectionManager): The ChromaDB collection manager.
        - chroma_collection (Collection): The ChromaDB collection.
    """

    chroma_collection_manager: ChromaDBCollectionManager
    chroma_collection: chroma_types.Collection


def setup_chroma(models: list[ModelType], logger: Logger) -> ChromaSetupReturnContext:
    chroma_settings = chroma_types.Settings(allow_reset=True)
    chroma_client: chroma_types.ClientAPI = chromadb.PersistentClient(
        settings=chroma_settings
    )
    chroma_client_manager = ChromaDBClientManager(chroma_client)

    logger.debug(f"Resetting Chroma client")
    if chroma_client_manager.reset_client():
        logger.debug("Client reset")

    chroma_collection: chroma_types.Collection = (
        chroma_client_manager.get_or_create_collection("postcode")
    )

    chroma_collection_manager = ChromaDBCollectionManager(chroma_collection)
    chroma_collection_manager.upsert_models(tuple(models))

    return ChromaSetupReturnContext(chroma_collection_manager, chroma_collection)
