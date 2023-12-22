from postcode.databases.arangodb.arangodb_builder import ArangoDBBuilder
from postcode.models import ModuleModel
from postcode.types.postcode import ModelType


class SummarizationMapper:
    def __init__(
        self,
        module_ids_to_update: list[str],
        module_models: tuple[ModuleModel, ...],
        arangodb_builder: ArangoDBBuilder,
    ) -> None:
        self.module_ids_to_update: list[str] = module_ids_to_update
        self.module_models: tuple[ModuleModel, ...] = module_models
        self.arangodb_builder: ArangoDBBuilder = arangodb_builder

        self.summarization_map: list[list[ModelType]] = []

    def create_summarization_map(self) -> list[list[ModelType]]:
        for module_id in self.module_ids_to_update:
            models_to_update: list[ModelType] = []

            upstream_models: list[
                ModelType
            ] | None = self.arangodb_builder.get_all_upstream_vertices(module_id)
            downstream_models: list[
                ModelType
            ] | None = self.arangodb_builder.get_all_downstream_vertices(module_id)

            ids_from_db: list[str] = []
            if upstream_models:
                upstream_ids_to_update: list[str] = [
                    model.id for model in upstream_models
                ]
                ids_from_db.extend(upstream_ids_to_update)

            ids_from_db.append(module_id)

            if downstream_models:
                downstream_ids_to_update: list[str] = [
                    model.id for model in downstream_models
                ]
                ids_from_db.extend(downstream_ids_to_update)

            for id in ids_from_db:
                for model in self.module_models:
                    if model.id == id:
                        models_to_update.append(model)
                    elif model.children:
                        for child in model.children:
                            if child.id == id:
                                models_to_update.append(child)

            self.summarization_map.append(models_to_update)

        return self.summarization_map
