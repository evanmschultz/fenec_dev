import logging
from pprint import pprint
from typing import Union
from postcode.databases.arangodb.arangodb_manager import ArangoDBManager
from postcode.models.models import (
    ClassModel,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)

# from postcode.types.postcode import ModelType

ModelType = Union[
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
]


class SummarizationMapper:
    def __init__(
        self,
        module_ids_to_update: list[str],
        module_models: tuple[ModuleModel, ...],
        arangodb_manager: ArangoDBManager,
    ) -> None:
        self.module_ids_to_update: list[str] = module_ids_to_update
        self.module_models: tuple[ModuleModel, ...] = module_models
        self.arangodb_manager: ArangoDBManager = arangodb_manager
        self.models_to_update: list[ModelType] = []
        self.model_visited_in_db: set[str] = set()
        self.summarization_map: list[ModelType] = []
        self.temp_map: list[ModelType] = []

    def _set_child_models_to_update(self, model: ModelType) -> None:
        if model.children_ids:
            for child in model.children_ids:
                # logging.info(f"Setting child model to update: {child.id}")
                self._set_child_models_to_update(child)
                child.summary = None
                self.models_to_update.append(child)
            self.models_to_update.append(model)

    def _set_models_to_update(self) -> None:
        for model in self.module_models:
            if model.id in self.module_ids_to_update:
                if model.children_ids:
                    for child in model.children_ids:
                        self._set_child_models_to_update(child)

                model.summary = None
                self.models_to_update.append(model)

    def _set_inbound_models_in_summarization_map(self, model_id: str) -> None:
        if model_id in self.model_visited_in_db:
            return
        self.model_visited_in_db.add(model_id)
        if inbound_models := self.arangodb_manager.get_inbound_models(model_id):
            for model in inbound_models:
                # logging.info(f"Setting inbound models in summarization map: {model.id}")
                self.model_visited_in_db.add(model_id)
                self._set_inbound_models_in_summarization_map(model.id)

                self.temp_map.append(model)

    def _set_outbound_models_in_summarization_map(self, model_id: str) -> None:
        if model_id in self.model_visited_in_db:
            return

        if outbound_models := self.arangodb_manager.get_outbound_models(model_id):
            for model in outbound_models[::-1]:
                # logging.info(
                #     f"Setting outbound models in summarization map: {model.id}"
                # )
                self.model_visited_in_db.add(model_id)
                # self._set_outbound_models_in_summarization_map(model.id)``

                if model.id in self.models_to_update:
                    model.summary = None
                self.temp_map.append(model)

    def create_summarization_map(self) -> list[ModelType]:
        self._set_models_to_update()
        logging.info("Set models to update")

        # pprint([model.id for model in self.models_to_update])

        for model in self.models_to_update:
            # self.model_visited_in_db = set()
            # logging.info(f"Setting inbound models in summarization map: {model.id}")
            self._set_inbound_models_in_summarization_map(model.id)
            self.temp_map.append(model)

            self.model_visited_in_db.remove(model.id)
            # logging.info(f"Setting outbound models in summarization map: {model.id}")
            # self._set_outbound_models_in_summarization_map(model.id)
            self.summarization_map.extend(self.temp_map)
            self.temp_map = []

        for model in self.models_to_update:
            self.model_visited_in_db = set()
            # logging.info(f"Setting outbound models in summarization map: {model.id}")
            self._set_outbound_models_in_summarization_map(model.id)
            self.summarization_map.extend(self.temp_map)
            self.temp_map = []

        logging.info("Created summarization map")
        summary_ids: set[str] = set()
        summary_map: list[ModelType] = []
        for model in self.summarization_map[::-1]:
            if model.id not in summary_ids:
                summary_map.append(model)
                summary_ids.add(model.id)

        # return summary_map[::-1]
        pprint([model.id for model in summary_map[::-1]])
        return summary_map[::-1]

    # def old_create_summarization_map(self) -> list[list[ModelType]]:
    #     for module_id in self.module_ids_to_update:
    #         models_to_update: list[ModelType] = []

    #         upstream_models: list[
    #             ModelType
    #         ] | None = self.arangodb_manager.get_all_upstream_vertices(module_id)
    #         downstream_models: list[
    #             ModelType
    #         ] | None = self.arangodb_manager.get_all_downstream_vertices(module_id)

    #         ids_from_db: list[str] = []
    #         if upstream_models:
    #             upstream_ids_to_update: list[str] = [
    #                 model.id for model in upstream_models
    #             ]
    #             ids_from_db.extend(upstream_ids_to_update)

    #         ids_from_db.append(module_id)

    #         if downstream_models:
    #             downstream_ids_to_update: list[str] = [
    #                 model.id for model in downstream_models
    #             ]
    #             ids_from_db.extend(downstream_ids_to_update)

    #         for id in ids_from_db:
    #             for model in self.module_models:
    #                 if model.id == id:
    #                     models_to_update.append(model)
    #                 elif model.children:
    #                     for child in model.children:
    #                         if child.id == id:
    #                             models_to_update.append(child)

    #         self.summarization_map.append(models_to_update)

    #     return self.summarization_map
