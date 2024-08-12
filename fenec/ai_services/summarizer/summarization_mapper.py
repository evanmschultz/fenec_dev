import logging
from fenec.databases.arangodb.arangodb_manager import ArangoDBManager
from fenec.types.fenec import ModelType


class SummarizationMapper:
    """
    A class for generating summarization maps based on specified module IDs and associated models.

    This class facilitates the creation of both bottom-up and top-down summarization maps by traversing
    inbound and outbound relationships in a graph structure. It utilizes an ArangoDBManager instance
    for querying relationships between models.

    Args:
        module_ids_to_update (list[str]): The list of module IDs to consider during summarization map creation.
        all_models (tuple[ModelType, ...]): Tuple of all models available for summarization.
        arangodb_manager (ArangoDBManager): The ArangoDBManager instance for handling database interactions.

    Methods:
        create_bottom_up_summarization_map(pass_num: int): Creates a bottom-up summarization map for the specified module IDs.
        create_top_down_summarization_map(pass_num: int): Creates a top-down summarization map for the specified module IDs.
    """

    def __init__(
        self,
        module_ids_to_update: list[str],
        all_models: tuple[ModelType, ...],
        arangodb_manager: ArangoDBManager,
    ) -> None:
        self.module_ids_to_update: list[str] = module_ids_to_update
        self.all_models: tuple[ModelType, ...] = all_models
        self.arangodb_manager: ArangoDBManager = arangodb_manager

        self.models_to_update: list[ModelType] = self._get_models_to_update()
        self.model_visited_in_db: set[str] = set()
        self.summarization_map: list[ModelType] = []
        self.temp_map: list[ModelType] = []

    def _get_models_to_update(self) -> list[ModelType]:
        """
        Returns all models that need to be updated based on the module IDs.

        This method queries the ArangoDBManager to find the models that are either directly associated with
        the module IDs or related through dependencies.

        Returns:
            list[ModelType]: List of models to be updated.
        """
        models_to_update: list[ModelType] = []
        for model in self.all_models:
            for module_id in self.module_ids_to_update:
                if module_id in model.id:
                    models_to_update.append(model)
                    break
        return models_to_update

    def _set_inbound_models_in_summarization_map(self, model_id: str) -> None:
        """
        Sets inbound models in the summarization map recursively.

        Args:
            model_id (str): The ID of the model.
        """
        if model_id in self.model_visited_in_db:
            return
        self.model_visited_in_db.add(model_id)
        inbound_models = self.arangodb_manager.get_inbound_models(model_id)
        if inbound_models:
            for model in inbound_models:
                self._set_inbound_models_in_summarization_map(model.id)
                self.temp_map.append(model)

    def _set_outbound_models_in_summarization_map(self, model_id: str) -> None:
        """
        Sets outbound models in the summarization map recursively.

        Args:
            model_id (str): The ID of the model.
        """
        if model_id in self.model_visited_in_db:
            return
        self.model_visited_in_db.add(model_id)
        outbound_models = self.arangodb_manager.get_outbound_models(model_id)
        if outbound_models:
            for model in outbound_models:
                self._set_outbound_models_in_summarization_map(model.id)
                self.temp_map.append(model)

    def create_bottom_up_summarization_map(self, pass_num: int) -> list[ModelType]:
        """
        Creates a bottom-up summarization map for the specified module IDs.

        This method creates a summarization map starting from the lowest-level models
        and working up to higher-level models by first traversing inbound relationships.

        Args:
            pass_num (int): The current pass number, used to differentiate between passes.

        Returns:
            list[ModelType]: The bottom-up summarization map.
        """
        logging.info(f"Creating bottom-up summarization map for pass {pass_num}")
        self._refresh_models_to_update()

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

        logging.info("Bottom-up summarization map created")
        return self._remove_duplicates(self.summarization_map)[::-1]

    def create_top_down_summarization_map(self, pass_num: int) -> list[ModelType]:
        """
        Creates a top-down summarization map for the specified module IDs.

        This method creates a summarization map starting from the highest-level models
        and working down to lower-level models by first traversing outbound relationships.

        Args:
            pass_num (int): The current pass number, used to differentiate between passes.

        Returns:
            list[ModelType]: The top-down summarization map.
        """
        logging.info(f"Creating top-down summarization map for pass {pass_num}")
        self._refresh_models_to_update()

        for model in self.models_to_update:
            logging.debug(f"Setting outbound models in summarization map: {model.id}")
            self._set_outbound_models_in_summarization_map(model.id)
            self.temp_map.append(model)
            self.model_visited_in_db.remove(model.id)
            self.summarization_map.extend(self.temp_map)
            self.temp_map = []

        for model in self.models_to_update:
            logging.debug(f"Setting inbound models in summarization map: {model.id}")
            self._set_inbound_models_in_summarization_map(model.id)
            self.summarization_map.extend(self.temp_map)
            self.temp_map = []

        logging.info("Top-down summarization map created")
        return self._remove_duplicates(self.summarization_map)

    def _remove_duplicates(self, summarization_map: list[ModelType]) -> list[ModelType]:
        """
        Removes duplicate models from the summarization map while preserving order.

        Args:
            summarization_map (list[ModelType]): The original summarization map.

        Returns:
            list[ModelType]: The summarization map with duplicates removed.
        """
        summary_ids: set[str] = set()
        unique_summary_map: list[ModelType] = []
        for model in summarization_map:
            if model.id not in summary_ids:
                unique_summary_map.append(model)
                summary_ids.add(model.id)
        return unique_summary_map

    def _refresh_models_to_update(self) -> None:
        """
        Refreshes the models_to_update list based on the current module_ids_to_update and all_models.

        This method re-queries the database via ArangoDBManager to get the correct list of models to process
        for either top-down or bottom-up summarization.
        """
        refreshed_models = []
        for module_id in self.module_ids_to_update:
            outbound_models = self.arangodb_manager.get_outbound_models(
                module_id
            )  # For top-down
            if outbound_models:
                refreshed_models.extend(outbound_models)

        self.models_to_update = (
            refreshed_models if refreshed_models else self.models_to_update
        )
