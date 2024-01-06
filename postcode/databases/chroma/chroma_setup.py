import logging

import chromadb
from postcode.databases.chroma.chromadb_client_manager import ChromaClientHandler

from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)

import postcode.types.chroma as chroma_types

from postcode.types.postcode import ModelType


def setup_chroma(collection_name: str = "postcode") -> ChromaCollectionManager:
    """
    Sets up and returns a Chroma Collection Manager.

    Args:
        - collection_name (str, optional): Name of the Chroma collection. Defaults to "postcode".

    Returns:
        - ChromaCollectionManager: An instance of ChromaCollectionManager for the specified collection.
    """

    chroma_settings = chroma_types.Settings(allow_reset=True)
    chroma_client: chroma_types.ClientAPI = chromadb.PersistentClient(
        settings=chroma_settings
    )
    chroma_client_manager = ChromaClientHandler(chroma_client)

    chroma_collection: chroma_types.Collection = (
        chroma_client_manager.get_or_create_collection(collection_name)
    )
    return ChromaCollectionManager(chroma_collection)


def setup_chroma_with_update(
    models: list[ModelType], collection_name: str = "postcode"
) -> ChromaCollectionManager:
    """
    Sets up Chroma with model updates and return a Chroma Collection Manager.

    Notes:
        - This will wipe the existing Chroma collection and replace it with the provided models.

    Args:
        - models (list[ModelType]): List of models to upsert into the Chroma collection.
        - collection_name (str, optional): Name of the Chroma collection. Defaults to "postcode".

    Returns:
        - ChromaCollectionManager: An instance of ChromaCollectionManager for the specified collection
          with the provided models upserted.
    """

    chroma_settings = chroma_types.Settings(allow_reset=True)
    chroma_client: chroma_types.ClientAPI = chromadb.PersistentClient(
        settings=chroma_settings
    )
    chroma_client_manager = ChromaClientHandler(chroma_client)

    logging.debug(f"Resetting Chroma client")
    if chroma_client_manager.reset_client():
        logging.debug("Client reset")

    chroma_collection: chroma_types.Collection = (
        chroma_client_manager.get_or_create_collection(collection_name)
    )
    chroma_collection_manager = ChromaCollectionManager(chroma_collection)
    chroma_collection_manager.upsert_models(tuple(models))
    logging.debug(f"Upserted models to Chroma collection {chroma_collection.name}")

    return chroma_collection_manager
