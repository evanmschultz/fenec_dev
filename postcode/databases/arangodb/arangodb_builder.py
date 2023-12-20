import json
from json import JSONEncoder
from typing import Any, Callable

from arango.result import Result
from arango.cursor import Cursor

from postcode.databases.arangodb.arangodb_manager import ArangoDBManager
from postcode.types.postcode import ModelType
from postcode.models import (
    ModuleModel,
    BlockType,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
)

# NOTE: Remember, when adding logic to connect dependencies, the `from` the external dependency `to` the internal definition using it


class GraphDBBuilder:
    def __init__(
        self, db_manager: ArangoDBManager, module_models: tuple[ModuleModel, ...]
    ) -> None:
        self.db_manager: ArangoDBManager = db_manager
        self.module_models: tuple[ModuleModel, ...] = module_models

        self.processed_id_set = set()

    def insert_models(self) -> None:
        for model in self.module_models:
            self._process_model(model)

    def _process_model(self, module_model: ModuleModel) -> None:
        self._create_vertex_for_module(module_model)
        self._process_children(module_model)

    def _create_vertex_for_module(self, module_model: ModuleModel) -> None:
        module_model._key = module_model.id
        module_data: dict[str, Any] = module_model.model_dump()
        module_data["_key"] = module_model.id

        try:
            self.db_manager.db.collection("modules").insert(module_data)
        except Exception as e:
            print(f"Error inserting {module_model.id} vertex (ArangoDB): {e}")

    def _process_children(self, parent_model: ModelType) -> None:
        if not parent_model.children:
            return

        for child in parent_model.children:
            if child.id in self.processed_id_set:
                print(f"Duplicate child key: {child.id}")
                continue
            self.processed_id_set.add(child.id)

            if isinstance(child, ClassModel):
                self._create_vertex_for_class(child)

            elif isinstance(child, FunctionModel):
                self._create_vertex_for_function(child)

            elif isinstance(child, StandaloneCodeBlockModel):
                self._create_vertex_for_standalone_block(child)

            if child.children:
                self._process_children(child)

    def _create_vertex(self, model: ModelType, vertex_type: str) -> None:
        if not model.parent_id:
            print(f"Error: No parent id found for {model.id}")
            return None

        try:
            vertex_type_str: str = (
                f"{vertex_type}s" if not vertex_type == "class" else f"{vertex_type}es"
            )
            model_data: dict[str, Any] = model.model_dump()
            model_data["_key"] = model.id
            self.db_manager.ensure_collection(f"{vertex_type_str}")
            self.db_manager.db.collection(f"{vertex_type_str}").insert(model_data)
            # print(f"{vertex_type.capitalize()} vertex created for {key}")

            parent_type: str = self._get_block_type_from_id(model.parent_id)
            self._create_edge(model.id, model.parent_id, vertex_type, parent_type)
        except Exception as e:
            print(f"Error inserting {vertex_type} vertex (ArangoDB): {e}")

    def _create_vertex_for_class(self, class_data: ClassModel) -> None:
        self._create_vertex(class_data, "class")

    def _create_vertex_for_function(self, function_data: FunctionModel) -> None:
        self._create_vertex(function_data, "function")

    def _create_vertex_for_standalone_block(
        self, standalone_block_data: StandaloneCodeBlockModel
    ) -> None:
        self._create_vertex(standalone_block_data, "standalone_block")

    def _create_edge(
        self, from_key: str, to_key: str, source_type: str, target_type: str
    ) -> None:
        source_string: str = (
            f"{source_type}s/{from_key}"
            if not source_type == "class"
            else f"{source_type}es/{from_key}"
        )
        target_string: str = (
            f"{target_type}s/{to_key}"
            if not target_type == "class"
            else f"{target_type}es/{to_key}"
        )
        edge_data: dict[str, str] = {
            "_from": f"{source_string}",
            "_to": f"{target_string}",
            "source_type": source_type,
            "target_type": target_type,
        }
        try:
            self.db_manager.ensure_edge_collection("code_edges")
            self.db_manager.db.collection("code_edges").insert(edge_data)
        except Exception as e:
            print(f"Error creating edge (ArangoDB): {e}")

    def _get_block_type_from_id(self, block_id: str) -> str:
        block_id_parts: list[str] = block_id.split("__*__")
        block_type_part: str = block_id_parts[-1]

        # Dictionary of callables
        block_type_functions: dict[str, Callable[..., str]] = {
            "MODULE": lambda: "module",
            "CLASS": lambda: "class",
            "FUNCTION": lambda: "function",
            "STANDALONE_BLOCK": lambda: "standalone_block",
        }

        # Iterate over the dictionary and call the function if the key is found in block_type_part
        for key, func in block_type_functions.items():
            if block_type_part.startswith(key):
                return func()

        return "unknown"

    def process_imports_and_dependencies(self) -> None:
        # Process each vertex in the database
        for vertex_collection in [
            "modules",
            "classes",
            "functions",
            "standalone_blocks",
        ]:
            cursor: Result[Cursor] = self.db_manager.db.collection(
                vertex_collection
            ).all()
            if isinstance(cursor, Cursor):
                for vertex in cursor:
                    vertex_key = vertex["_key"]
                    if vertex_collection == "modules":
                        self._create_edges_for_imports(
                            vertex_key, vertex.get("imports", [])
                        )
                    else:
                        self._create_edges_for_dependencies(
                            vertex_key, vertex.get("dependencies", [])
                        )
            else:
                print(
                    f"Error getting cursor for vertex collection: {vertex_collection}"
                )

    def _create_edges_for_imports(
        self, module_key: str, imports: list[dict[str, Any]]
    ) -> None:
        if not imports:
            print(f"No imports found for module {module_key}")
            return

        print(f"Processing imports for module {module_key}")

        for imp in imports:
            import_names = imp.get("import_names", [])
            if not import_names:
                print(f"No import names found in import {imp}")
                continue

            for import_name in import_names:
                local_block_id = import_name.get("local_block_id")

                if local_block_id:
                    print(f"\nLocal block id: {local_block_id}")
                    target_type = self._get_block_type_from_id(local_block_id)
                    try:
                        self._create_edge(
                            module_key, local_block_id, "module", target_type
                        )
                        print(
                            f"Created edge for import {module_key} to {local_block_id}"
                        )
                    except Exception as e:
                        print(
                            f"Error creating edge for import {module_key} to {local_block_id}: {e}"
                        )
                else:
                    print(f"Skipped import {import_name} in module {module_key}")

    def _create_edges_for_dependencies(
        self, block_key: str, dependencies: list[dict[str, Any]]
    ) -> None:
        if not dependencies:
            return

        for dependency in dependencies:
            code_block_id = dependency.get("code_block_id")
            if code_block_id:
                source_type: str = self._get_block_type_from_id(block_key)
                target_type: str = self._get_block_type_from_id(code_block_id)
                try:
                    self._create_edge(
                        block_key, code_block_id, source_type, target_type
                    )
                except Exception as e:
                    print(
                        f"Error creating edge for dependency {block_key} to {code_block_id}: {e}"
                    )
