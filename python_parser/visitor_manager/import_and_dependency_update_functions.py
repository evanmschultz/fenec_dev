# TODO: Add logic to update imports when defined in a StandaloneCodeBlock
# TODO: Add logic to track down the import's definition location

from model_builders.module_model_builder import ModuleModelBuilder
from models.enums import ImportModuleType
from models.models import ImportModel, ImportNameModel


class ImportAndDependencyUpdateFunctions:
    def __init__(self, model_builder_list: list[ModuleModelBuilder]) -> None:
        self.model_builder_list: list[ModuleModelBuilder] = model_builder_list

    def update_imports(self) -> None:
        for model_builder in self.model_builder_list:
            self.process_builder(model_builder)

    def process_builder(self, builder: ModuleModelBuilder) -> None:
        if module_imports := builder.module_attributes.imports:
            self.handle_import_models(builder, module_imports)

    def handle_import_models(
        self, builder: ModuleModelBuilder, module_imports: list[ImportModel]
    ) -> None:
        module_imports_tuple = tuple(
            module_imports
        )  # HACK: To prevent missing elements as the list was getting modified during iteration

        for import_model in module_imports_tuple:
            self.update_import_for_builder(builder, import_model)

    def update_import_for_builder(
        self, builder: ModuleModelBuilder, import_model: ImportModel
    ) -> None:
        if self.is_local_import(import_model, builder.id):
            import_path: str = self.get_import_path(import_model)
            import_names: list[str] | None = None

            if import_model.imported_from:
                import_names = self.get_import_names(import_model)
            else:
                import_path: str = self.get_import_path(import_model)

            for external_builder in self.model_builder_list:
                if self.should_skip_builder(
                    builder, external_builder, import_path, import_model
                ):
                    continue

                self.update_import_model(
                    import_model, import_names, builder, external_builder
                )

    def is_local_import(self, import_model: ImportModel, builder_id: str) -> bool:
        return import_model.import_module_type == ImportModuleType.LOCAL

    def get_import_names(self, import_model: ImportModel) -> list[str]:
        return [name.name for name in import_model.import_names]

    def get_import_path(self, import_model: ImportModel) -> str:
        if import_model.imported_from:
            return import_model.imported_from.replace(".", "/")
        else:
            return import_model.import_names[0].name.replace(".", "/")

    def should_skip_builder(
        self,
        builder: ModuleModelBuilder,
        external_builder: ModuleModelBuilder,
        import_path: str,
        import_model: ImportModel,
    ) -> bool:
        return (
            external_builder.id == builder.id
            or not import_path in external_builder.id
            or import_model.local_module_id is not None
        )

    def update_import_model(
        self,
        import_model: ImportModel,
        import_names: list[str] | None,
        builder: ModuleModelBuilder,
        external_builder: ModuleModelBuilder,
    ) -> None:
        new_import_model: ImportModel = import_model.model_copy()
        new_import_model.local_module_id = external_builder.id

        if not import_model.imported_from:
            builder.update_import(new_import_model, import_model)
            return

        if import_names:
            new_import_name_models: list[
                ImportNameModel
            ] = self.get_new_import_name_models(
                external_builder, import_names, import_model
            )

            if len(new_import_name_models) < len(import_model.import_names):
                # TODO: Add logic to track down the import's definition location

                new_import_name_models = self.add_missing_imports(
                    new_import_name_models, import_model.import_names
                )

            new_import_model.import_names = new_import_name_models
            builder.update_import(new_import_model, import_model)

    def get_new_import_name_models(
        self,
        external_builder: ModuleModelBuilder,
        import_names: list[str],
        import_model: ImportModel,
    ) -> list[ImportNameModel]:
        new_import_name_models: list = []
        for child_builder in external_builder.children_builders:
            for import_name in import_names:
                child_builder_id_split: list[str] = child_builder.id.split("-")

                if import_name == child_builder_id_split[-1]:
                    for import_name_model in import_model.import_names:
                        if import_name_model.name == import_name:
                            new_import_name_model: ImportNameModel = (
                                import_name_model.model_copy()
                            )

                            new_import_name_model.local_block_id = child_builder.id
                            new_import_name_models.append(new_import_name_model)
                            break

        return new_import_name_models

    def add_missing_imports(
        self,
        new_import_name_models: list[ImportNameModel],
        existing_import_names: list[ImportNameModel],
    ) -> list[ImportNameModel]:
        for import_name_model in existing_import_names:
            if import_name_model.name not in [
                name.name for name in new_import_name_models
            ]:
                new_import_name_models.append(import_name_model)

        return new_import_name_models
