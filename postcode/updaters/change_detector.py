from postcode.databases.arangodb.arangodb_manager import ArangoDBManager
from postcode.models.models import ModuleModel
from postcode.types.postcode import ModelType


class ChangeDetector:
    def __init__(
        self, all_models: tuple[ModelType, ...], arangodb_manager: ArangoDBManager
    ) -> None:
        self.all_models: tuple[ModelType, ...] = all_models
        self.id_to_model: dict[str, ModelType] = {
            model.id: model for model in all_models
        }
        self.arangodb_manager: ArangoDBManager = arangodb_manager

    def get_affected_models(
        self, changed_files: list[str], both_directions: bool = False
    ) -> set[str]:
        affected_models = set()

        for model in self.all_models:
            if isinstance(model, ModuleModel) and model.file_path in changed_files:
                affected_models.add(model.id)
                affected_models.update(
                    self._get_connected_models(model.id, both_directions)
                )

        return affected_models

    def _get_connected_models(self, model_id: str, both_directions: bool) -> set[str]:
        connected_models = set()

        # Get outbound models (dependencies and children)
        outbound_models: list[ModelType] | None = (
            self.arangodb_manager.get_outbound_models(model_id)
        )
        if outbound_models:
            connected_models.update(model.id for model in outbound_models)

        if both_directions:
            # Get inbound models (dependents and parents)
            inbound_models: list[ModelType] | None = (
                self.arangodb_manager.get_inbound_models(model_id)
            )
            if inbound_models:
                connected_models.update(model.id for model in inbound_models)

        return connected_models
