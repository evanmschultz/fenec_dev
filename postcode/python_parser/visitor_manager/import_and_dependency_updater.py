# TODO: Add logic to update imports when defined in a StandaloneCodeBlock
# TODO: Add logic to track down the import's definition location
# FIXME: There is still an issue with the imports being updated twice for some reason

from postcode.python_parser.model_builders.module_model_builder import (
    ModuleModelBuilder,
)
from postcode.models.models import (
    DependencyModel,
    ImportModel,
    ImportNameModel,
    ImportModuleType,
)


class ImportAndDependencyUpdater:
    """
    The ImportAndDependencyUpdater class is designed to update import statements and
    dependencies in a set of module model builders. It manages two main tasks: updating
    import statements using an ImportUpdater and updating dependencies using a DependencyUpdater.
    This class ensures that both imports and dependencies are consistent and up-to-date
    across the provided module model builders.

    Attributes:
        model_builder_list (list[ModuleModelBuilder]): A list of ModuleModelBuilder instances
        to be processed for import and dependency updates.

    Example:
        model_builders = [ModuleModelBuilder(), ModuleModelBuilder()]
        updater = ImportAndDependencyUpdater(model_builders)
        updater.update_imports()
    """

    def __init__(self, model_builder_tuple: tuple[ModuleModelBuilder, ...]) -> None:
        self.model_builder_tuple: tuple[ModuleModelBuilder, ...] = model_builder_tuple

    def update_imports(self) -> None:
        """
        Processes each module model builder in the model_builder_list and updates their import
        statements. This method is the primary entry point for initiating the import update process.

        Example:
            updater = ImportAndDependencyUpdater(model_builders)
            updater.update_imports()
        """

        for model_builder in self.model_builder_tuple:
            import_updater: ImportUpdater = ImportUpdater(self.model_builder_tuple)
            import_updater.process_builder(model_builder)

            # for model_builder in self.model_builder_tuple:
            ...
        # Track down and add imports for the imports that were defined outside of the module that it is imported from


class ImportUpdater:
    """
    The ImportUpdater class is designed to manage and update import statements across
    a collection of module model builders. It processes each builder in the provided
    list, handling and updating import models as required. This class plays a crucial
    role in ensuring that import statements are correctly managed and updated in response
    to changes in the module models.

    Attributes:
        model_builder_list (list[ModuleModelBuilder]): A list of ModuleModelBuilder
        instances to be processed for import updates.

    Example:
        model_builders = [ModuleModelBuilder(), ModuleModelBuilder()]
        import_updater = ImportUpdater(model_builders)
        for builder in model_builders:
            import_updater.process_builder(builder)
    """

    def __init__(self, model_builder_tuple: tuple[ModuleModelBuilder, ...]) -> None:
        self.model_builder_tuple: tuple[ModuleModelBuilder, ...] = model_builder_tuple

    def process_builder(self, builder: ModuleModelBuilder) -> None:
        """
        Processes a single module model builder to update its import statements.

        Args:
            builder (ModuleModelBuilder): The module model builder to process.
        """

        if module_imports := builder.module_attributes.imports:
            module_imports_tuple = tuple(module_imports)
            self._handle_import_models(builder, module_imports_tuple)
            # print(module_imports_tuple)

    def _handle_import_models(
        self, builder: ModuleModelBuilder, module_imports_tuple: tuple[ImportModel, ...]
    ) -> None:
        """
        Handles the import models for a given builder and updates them as necessary.

        Args:
            builder (ModuleModelBuilder): The builder whose import models are to be handled.
            module_imports (tuple[ImportModel]): A tuple of import models to process.
        """

        # module_imports_tuple = tuple(module_imports)
        # # HACK: Converts to tuple in order to prevent missing elements as the list was getting modified during iteration

        for import_model in module_imports_tuple:
            self._update_import_for_builder(builder, import_model)

            DependencyUpdater.update_dependencies(builder)

    def _update_import_for_builder(
        self, builder: ModuleModelBuilder, import_model: ImportModel
    ) -> None:
        """
        Updates a single import model for the given builder. Determines if the import is local,
        and if so, updates the import path and names accordingly.

        Args:
            builder (ModuleModelBuilder): The builder that owns the import model.
            import_model (ImportModel): The import model to be updated.
        """

        if self._is_local_import(import_model):
            import_path: str = self._get_import_path(import_model)
            import_names: list[str] | None = None

            if import_model.imported_from:
                import_names = self._get_import_names(import_model)
            # else:
            #     import_path: str = self._get_import_path(import_model)

            for external_builder in self.model_builder_tuple:
                if self._should_skip_builder(
                    builder, external_builder, import_path, import_model
                ):
                    continue

                self._update_import_model(
                    import_model, import_names, builder, external_builder
                )

    def _is_local_import(self, import_model: ImportModel) -> bool:
        """Returns True if the import is local."""
        return import_model.import_module_type == ImportModuleType.LOCAL

    def _get_import_names(self, import_model: ImportModel) -> list[str]:
        """Returns a list of import names for the given import model."""
        return [name.name for name in import_model.import_names]

    def _get_import_path(self, import_model: ImportModel) -> str:
        """Returns the import path for the given import model."""

        if import_model.imported_from:
            return import_model.imported_from.replace(".", ":")
        else:
            return import_model.import_names[0].name.replace(".", ":")

    def _should_skip_builder(
        self,
        builder: ModuleModelBuilder,
        external_builder: ModuleModelBuilder,
        import_path: str,
        import_model: ImportModel,
    ) -> bool:
        """Returns boolean indicating if the given builder should be skipped."""

        return (
            external_builder.id == builder.id
            or not import_path in external_builder.id
            or import_model.local_module_id is not None
        )

    def _update_import_model(
        self,
        import_model: ImportModel,
        import_names: list[str] | None,
        builder: ModuleModelBuilder,
        external_builder: ModuleModelBuilder,
    ) -> None:
        """
        Updates the import model with new import names and assigns the local module ID to the external builder.

        Args:
            import_model (ImportModel): The import model to be updated.
            import_names (list[str] | None): The list of new import names.
            builder (ModuleModelBuilder): The module model builder.
            external_builder (ModuleModelBuilder): The external module model builder.

        Returns:
            None
        """
        new_import_model: ImportModel = import_model.model_copy()
        new_import_model.local_module_id = external_builder.id

        if not import_model.imported_from:
            builder.update_import(new_import_model, import_model)
            return

        if import_names:
            new_import_name_models: list[
                ImportNameModel
            ] = self._get_new_import_name_models(
                external_builder, import_names, import_model
            )
            # print(f"{len(new_import_name_models)} : {len(import_model.import_names)}")
            if len(new_import_name_models) < len(import_model.import_names):
                # TODO: Add logic to track down the import's definition location

                new_import_name_models = self._add_missing_imports(
                    new_import_name_models, import_model.import_names
                )

            new_import_model.import_names = new_import_name_models
            builder.update_import(new_import_model, import_model)

    def _get_new_import_name_models(
        self,
        external_builder: ModuleModelBuilder,
        import_names: list[str],
        import_model: ImportModel,
    ) -> list[ImportNameModel]:
        """
        Returns a list of new ImportNameModel objects based on the given import names.

        Args:
            external_builder (ModuleModelBuilder): The external module builder.
            import_names (list[str]): The list of import names.
            import_model (ImportModel): The import model.

        Returns:
            list[ImportNameModel]: The list of new ImportNameModel objects.
        """

        new_import_name_models: list = []
        for child_builder in external_builder.child_builders:
            for import_name in import_names:
                child_builder_id_split: list[str] = child_builder.id.split("-")

                if import_name == child_builder_id_split[-1]:
                    for import_name_model in import_model.import_names:
                        if import_name_model.name == import_name:
                            new_import_name_model: ImportNameModel = (
                                import_name_model.model_copy()
                            )
                            # if import_name_model.name == "OpenAISummarizer":
                            #     print(f"Found OpenAISummarizer: id")

                            new_import_name_model.local_block_id = child_builder.id
                            new_import_name_models.append(new_import_name_model)
                            break

        return new_import_name_models

    def _add_missing_imports(
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


class DependencyUpdater:
    """
    Class responsible for updating dependencies in a module.

    Methods:
        - `update_dependencies` (staticmethod): Updates the dependencies in the module.

    Examples:
        ```Python
        model_builder = ModuleModelBuilder()

        DependencyUpdater.update_dependencies(model_builder)
        ```
    """

    @staticmethod
    def update_dependencies(model_builder: ModuleModelBuilder) -> None:
        """
        Updates the dependencies in the module.

        Args:
            - model_builder (ModuleModelBuilder): The module model builder to update the dependencies for.

        Returns:
            - None

        Example:
            ```Python
            model_builder = ModuleModelBuilder()

            DependencyUpdater.update_dependencies(model_builder)
            ```
        """
        import_model_list: list[
            ImportModel
        ] | None = model_builder.module_attributes.imports
        if model_builder.child_builders:
            for child_builder in model_builder.child_builders:
                if (
                    not child_builder.common_attributes.dependencies
                    or not import_model_list
                ):
                    continue

                dependencies_to_process: tuple[
                    ImportModel | DependencyModel, ...
                ] = tuple(child_builder.common_attributes.dependencies)
                imports_to_process: tuple[ImportModel, ...] = tuple(import_model_list)
                for dependency in dependencies_to_process:
                    if isinstance(dependency, DependencyModel):
                        continue

                    dependency_import_names: list[str] = [
                        name.name for name in dependency.import_names
                    ]

                    for import_model in imports_to_process:
                        import_model_import_names: list[str] = [
                            name.name for name in import_model.import_names
                        ]

                        if (
                            dependency_import_names == import_model_import_names
                            and dependency.imported_from == import_model.imported_from
                        ):
                            child_builder.update_import_dependency(
                                import_model, dependency
                            )
                            break
