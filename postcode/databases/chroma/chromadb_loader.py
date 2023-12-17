import logging
from typing import Any, Mapping

from postcode.types.postcode import ModelType

from postcode.python_parser.models.models import ModuleModel
from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaDBCollectionManager,
)


class ChromaDBLoader:
    def __init__(
        self,
        module_models: tuple[ModuleModel, ...],
        collection_manager: ChromaDBCollectionManager,
    ) -> None:
        self.module_models: tuple[ModuleModel, ...] = module_models
        self.collection_manager: ChromaDBCollectionManager = collection_manager

    def load_models(self) -> None:
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[Mapping[str, str | int | float | bool]] = []

        for module_model in self.module_models:
            ids.append(module_model.id)
            documents.append(module_model.code_content)
            metadatas.append(module_model.convert_to_metadata())

            if module_model.children:
                for child in module_model.children:
                    ids.append(child.id)
                    documents.append(child.code_content)
                    metadatas.append(child.convert_to_metadata())

        logging.info(
            f"{self.collection_manager.collection.name} has {self.collection_manager.collection_embedding_count()} embeddings."
        )
        self.collection_manager.upsert_documents(
            ids=ids, documents=documents, metadatas=metadatas
        )
        logging.info(
            f"After upsert {self.collection_manager.collection.name} has {self.collection_manager.collection_embedding_count()} embeddings."
        )
