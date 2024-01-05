import logging
from postcode.databases.arangodb.arangodb_manager import ArangoDBManager

from postcode.types.postcode import ModelType


class SummarizationMapper:
    def __init__(
        self,
        module_ids_to_update: list[str],
        all_models: tuple[ModelType, ...],
        arangodb_manager: ArangoDBManager,
    ) -> None:
        self.module_ids_to_update: list[str] = module_ids_to_update
        self.all_models: tuple[ModelType, ...] = all_models
        self.arangodb_manager: ArangoDBManager = arangodb_manager

        self.models_to_update: list[ModelType] = self._set_models_to_update()
        self.model_visited_in_db: set[str] = set()
        self.summarization_map: list[ModelType] = []
        self.temp_map: list[ModelType] = []

    def _set_models_to_update(self) -> list[ModelType]:
        """Returns all models that need to be updated."""

        models_to_update: list[ModelType] = []
        for model in self.all_models:
            for module_id in self.module_ids_to_update:
                if module_id in model.id:
                    models_to_update.append(model)
                    break

        return models_to_update

    def _set_inbound_models_in_summarization_map(self, model_id: str) -> None:
        if model_id in self.model_visited_in_db:
            return
        self.model_visited_in_db.add(model_id)
        if inbound_models := self.arangodb_manager.get_inbound_models(model_id):
            for model in inbound_models:
                self.model_visited_in_db.add(model_id)
                self._set_inbound_models_in_summarization_map(model.id)

                self.temp_map.append(model)

    def _set_outbound_models_in_summarization_map(self, model_id: str) -> None:
        if model_id in self.model_visited_in_db:
            return

        if outbound_models := self.arangodb_manager.get_outbound_models(model_id):
            for model in outbound_models[::-1]:
                self.model_visited_in_db.add(model_id)

                if model.id in self.models_to_update:
                    model.summary = None
                self.temp_map.append(model)

    def create_summarization_map(self) -> list[ModelType]:
        self._set_models_to_update()
        logging.info("Set models to update")

        for model in self.models_to_update:
            logging.debug(f"Setting inbound models in summarization map: {model.id}")
            self._set_inbound_models_in_summarization_map(model.id)
            self.temp_map.append(model)

            self.model_visited_in_db.remove(model.id)
            self.summarization_map.extend(self.temp_map)
            self.temp_map = []

        for model in self.models_to_update:
            logging.debug(f"Setting outbound models in summarization map: {model.id}")
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

        return summary_map[::-1]
