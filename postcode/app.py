import logging
from logging import Logger
from typing import Union

from postcode.models.models import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
)

from postcode.databases.chroma.setup_chroma import (
    ChromaSetupReturnContext,
)
from postcode.updaters.graph_db_updater import GraphDBUpdater

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]

from postcode.utilities.logger.logging_config import setup_logging

from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaDBCollectionManager,
)

from chromadb.api.types import (
    QueryResult,
)
from chromadb import Collection

from postcode.updaters.standard_updater import StandardUpdater


def query_chroma(
    query: str,
    chroma_collection_manager: ChromaDBCollectionManager,
    chroma_collection: Collection,
    logger: Logger,
) -> None:
    logger.info(f"Querying ChromaDB collection {chroma_collection.name}")
    results: QueryResult | None = chroma_collection_manager.query_collection(
        [query],
        n_results=10,
        # where_filter={"block_type": "MODULE"},
        include_in_result=["metadatas", "documents", "embeddings"],
    )
    logger.info("Query results:")
    if results:
        if results["ids"]:
            for document in results["ids"][0]:
                print(document)

            print(f"Total results: {len(results['ids'][0])}")


def main(
    directory: str = ".",
    output_directory: str = "output_json",
) -> None:
    setup_logging()
    logger: Logger = logging.getLogger(__name__)

    #   ==================== GraphDB ====================
    graph_db_updater = GraphDBUpdater(directory, output_directory, logger)
    chroma_context: ChromaSetupReturnContext = graph_db_updater.update_all(
        directory, output_directory, logger
    )
    # ==================== End GraphDB ====================

    #   ==================== Standard ====================
    # chroma_context: ChromaSetupReturnContext = StandardUpdater.update_all(
    #     directory, output_directory, logger
    # )
    # ==================== End Standard ====================

    # query: str = "summarizes code block"
    # query_chroma(
    #     query,
    #     chroma_context.chroma_collection_manager,
    #     chroma_context.chroma_collection,
    #     logger,
    # )
