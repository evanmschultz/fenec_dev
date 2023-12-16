import json
import os
from arango.result import Result
from arango.typings import Json
from arango.cursor import Cursor

from typing import Any

from arango_db.arango_db_manager import ArangoDBManager

# NOTE: Remember, when adding logic to connect dependencies, the `from` the external dependency `to` the internal definition using it


class GraphDBBuilder:
    def __init__(self, db_manager: ArangoDBManager) -> None:
        self.db_manager: ArangoDBManager = db_manager
        self.processed_id_set = set()

    def process_json_directory(self, directory_path: str) -> None:
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path: str = os.path.join(directory_path, filename)
                # print(f"Processing file: {file_path}")
                try:
                    with open(file_path, "r") as file:
                        json_data = json.load(file)
                        self.process_json_data(json_data)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    def process_json_data(self, json_data: dict[str, Any]) -> None:
        if json_data.get("block_type") == "MODULE":
            module_id: str | None = json_data.get("id")
            self.create_vertex_for_module(json_data)
            if module_id:
                self.process_children(json_data, module_id)

    def create_vertex_for_module(self, module_data: dict[str, Any]) -> None:
        if "_key" not in module_data and "id" in module_data:
            module_data["_key"] = module_data["id"]

        # print(f"Creating module vertex with attributes: {module_data['_key']}")
        try:
            response: Result[bool | Json] = self.db_manager.db.collection(
                "modules"
            ).insert(module_data)
            # print(f"Module vertex created, response: {response}")
        except Exception as e:
            print(f"Error inserting module vertex (ArangoDB): {e}")

    count = 0

    def process_children(self, parent_data: dict[str, Any], parent_key: str) -> None:
        children = parent_data.get("children")
        if not isinstance(children, list):
            return

        for child in parent_data.get("children", []):
            child_key = child.get("id")
            child_block_type = child.get("block_type")
            if child_key:
                if child_key in self.processed_id_set:
                    print(f"Duplicate child key: {child_key}")
                    continue
                self.processed_id_set.add(child_key)

            if child_block_type == "CLASS":
                self.create_vertex_for_class(child, parent_key)

            elif child_block_type == "FUNCTION":
                self.create_vertex_for_function(child, parent_key)

            elif child_block_type == "STANDALONE_BLOCK":
                self.create_vertex_for_standalone_block(child, parent_key)

            if child_key and "children" in child:
                self.count += 1
                self.process_children(child, child_key)

        # print(f"Total children: {self.count}")
        # print(f"Total unique children: {len(self.processed_id_set)}")

    def create_vertex(
        self, data: dict[str, Any], parent_key: str, vertex_type: str
    ) -> None:
        key: str | None = data.get("id")
        if "_key" not in data and key:
            data["_key"] = key
        data["parent_id"] = parent_key

        # print(f"Creating {vertex_type} vertex with attributes: {data['_key']}")
        try:
            vertex_type_str: str = (
                f"{vertex_type}s" if not vertex_type == "class" else f"{vertex_type}es"
            )
            self.db_manager.ensure_collection(f"{vertex_type_str}")
            self.db_manager.db.collection(f"{vertex_type_str}").insert(data)
            # print(f"{vertex_type.capitalize()} vertex created for {key}")

            if key:
                parent_type: str = self.get_block_type_from_id(parent_key)
                self.create_edge(key, parent_key, vertex_type, parent_type)
        except Exception as e:
            print(f"Error inserting {vertex_type} vertex (ArangoDB): {e}")

    def create_vertex_for_class(
        self, class_data: dict[str, Any], parent_key: str
    ) -> None:
        self.create_vertex(class_data, parent_key, "class")

    def create_vertex_for_function(
        self, function_data: dict[str, Any], parent_key: str
    ) -> None:
        self.create_vertex(function_data, parent_key, "function")

    def create_vertex_for_standalone_block(
        self, standalone_block_data: dict[str, Any], parent_key: str
    ) -> None:
        self.create_vertex(standalone_block_data, parent_key, "standalone_block")

    def create_edge(
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
            # print(f"Edge created between {from_key} and {to_key}")
        except Exception as e:
            print(f"Error creating edge (ArangoDB): {e}")

    def get_block_type_from_id(self, block_id) -> str:
        block_id_parts: list[str] = block_id.split("__*__")

        block_type_part: str = block_id_parts[-1]
        if block_type_part.startswith("MODULE"):
            return "module"
        elif block_type_part.startswith("CLASS"):
            return "class"
        elif block_type_part.startswith("FUNCTION"):
            return "function"
        elif block_type_part.startswith("STANDALONE_BLOCK"):
            return "standalone_block"
        else:
            return "unknown"

    def process_imports_and_dependencies(self):
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
                        self.create_edges_for_imports(
                            vertex_key, vertex.get("imports", [])
                        )
                    else:
                        self.create_edges_for_dependencies(
                            vertex_key, vertex.get("dependencies", [])
                        )
            else:
                print(
                    f"Error getting cursor for vertex collection: {vertex_collection}"
                )

    def create_edges_for_imports(
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

            for imp_name in import_names:
                local_block_id = imp_name.get("local_block_id")

                if local_block_id:
                    print(f"\nLocal block id: {local_block_id}")
                    target_type = self.get_block_type_from_id(local_block_id)
                    try:
                        self.create_edge(
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
                    print(f"Skipped import {imp_name} in module {module_key}")

    def create_edges_for_dependencies(
        self, block_key: str, dependencies: list[dict[str, Any]]
    ) -> None:
        if not dependencies:
            return

        for dependency in dependencies:
            code_block_id = dependency.get("code_block_id")
            if code_block_id:
                source_type = self.get_block_type_from_id(block_key)
                target_type = self.get_block_type_from_id(code_block_id)
                try:
                    self.create_edge(block_key, code_block_id, source_type, target_type)
                except Exception as e:
                    print(
                        f"Error creating edge for dependency {block_key} to {code_block_id}: {e}"
                    )


if __name__ == "__main__":
    # Example usage
    db_manager = ArangoDBManager()
    db_manager.delete_all_collections()  # Delete all collections in the database
    db_manager.setup_collections()  # Create the required collections
    graph_builder = GraphDBBuilder(db_manager)

    # Directory containing JSON files
    json_directory = "/Users/evanschultz/Documents/Code/post-code/output/json/"

    # Process all JSON files in the directory
    graph_builder.process_json_directory(json_directory)
    graph_builder.process_imports_and_dependencies()
