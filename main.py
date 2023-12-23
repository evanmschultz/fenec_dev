import logging
from logging import Logger
from pprint import pprint

from openai import OpenAI
import chromadb
from chromadb.config import Settings
from postcode.ai_services.summarizer.summarization_mapper import SummarizationMapper
from postcode.databases.arangodb.arangodb_manager import ArangoDBManager
from postcode.databases.arangodb.arangodb_connector import ArangoDBConnector

import postcode.types.chroma as chroma_types

from postcode.ai_services.summarizer.summarization_manager import SummarizationManager
from postcode.json_management.json_handler import JSONHandler
from postcode.models import ModuleModel
from postcode.types.postcode import ModelType

from postcode.utilities.logger.logging_config import setup_logging
from postcode.python_parser.visitor_manager.visitor_manager import (
    VisitorManager,
    VisitorManagerProcessFilesReturn,
)
from postcode.ai_services.summarizer.summarizer import OpenAISummarizer

from postcode.databases.chroma import (
    ChromaDBClientManager,
    ChromaDBCollectionManager,
)


def setup_chroma() -> (
    tuple[ChromaDBCollectionManager, chroma_types.Collection, ChromaDBClientManager]
):
    chroma_settings = Settings(allow_reset=True)
    chroma_client: chroma_types.ClientAPI = chromadb.PersistentClient(
        settings=chroma_settings
    )
    chroma_client_manager = ChromaDBClientManager(chroma_client)
    chroma_collection: chroma_types.Collection = (
        chroma_client_manager.get_or_create_collection("postcode")
    )

    return (
        ChromaDBCollectionManager(chroma_collection),
        chroma_collection,
        chroma_client_manager,
    )


def upsert_models(
    chroma_collection_manager: ChromaDBCollectionManager,
    module_models: tuple[ModuleModel, ...],
) -> None:
    chroma_collection_manager.upsert_models(module_models)


def query_chroma(
    query: str,
    chroma_collection_manager: ChromaDBCollectionManager,
    chroma_collection: chroma_types.Collection,
    logger: Logger,
) -> None:
    logger.info(f"Querying ChromaDB collection {chroma_collection.name}")
    results: chroma_types.QueryResult | None = chroma_collection_manager.query_collection(
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


def delete_collection(
    chroma_client_manager: ChromaDBClientManager, logger: Logger
) -> None:
    logger.info("Collections list", chroma_client_manager.list_collections())
    chroma_client_manager.delete_collection("postcode")
    logger.info("Collections list", chroma_client_manager.list_collections())


def reset_chroma_client(
    chroma_client_manager: ChromaDBClientManager, logger: Logger
) -> None:
    if chroma_client_manager.reset_client():
        logger.info("Client reset")


def parse_and_summarize(
    directory: str, output_directory: str, logger: Logger
) -> tuple[ModuleModel, ...]:
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
    finalized_module_models: tuple[
        ModuleModel, ...
    ] = summarization_manager.create_and_add_summaries_to_models()
    # print(finalized_module_models)
    logger.info("Summarization complete")

    logger.info("Saving models as JSON")
    json_manager = JSONHandler(directory, directory_modules, output_directory)

    for module_model in module_models_tuple:
        json_manager.save_model_as_json(module_model, module_model.file_path)

    json_manager.save_visited_directories()
    logger.info("JSON save complete")

    logger.info("Directory parsing completed.")

    return finalized_module_models


def main(
    directory: str = ".",
    output_directory: str = "output",
) -> None:
    logger: Logger = logging.getLogger(__name__)

    # (
    #     chroma_collection_manager,
    #     chroma_collection,
    #     chroma_client_manager,
    # ) = setup_chroma()

    module_models: tuple[ModuleModel, ...] = parse_and_summarize(
        directory, output_directory, logger
    )
    # upsert_models(chroma_collection_manager, module_models)
    # query: str = "class and functions"
    # query_chroma(query, chroma_collection_manager, chroma_collection, logger)
    # delete_collection(chroma_client_manager, logger)
    # reset_chroma_client(chroma_client_manager, logger)

    db_manager = ArangoDBConnector()
    db_manager.delete_all_collections()  # Delete all collections in the database
    db_manager.ensure_collections()  # Create the required collections

    graph_manager = ArangoDBManager(db_manager)
    graph_manager.insert_models(
        list(module_models)
    ).process_imports_and_dependencies().get_or_create_graph()

    summarization_map: list[ModelType] = SummarizationMapper(
        [
            "postcode:ai_services:summarizer:summarization_mapper.py__*__MODULE",
            "postcode:types:postcode.py__*__MODULE",
        ],
        module_models,
        graph_manager,
    ).create_summarization_map()

    # models_to_update: list[ModelType] = []
    # for models in summarization_map:
    #     models_to_update.extend(models)

    summary_list = []
    for model in summarization_map:
        summary_list.append(model.id)
    pprint([model.id for model in summarization_map])
    print(len(summary_list))


if __name__ == "__main__":
    setup_logging()
    main()
