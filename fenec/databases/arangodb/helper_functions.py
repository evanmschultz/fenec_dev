from fenec.models.enums import BlockType
from fenec.models.models import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    StandaloneCodeBlockModel,
    DirectoryModel,
)

from fenec.types.fenec import ModelType


def pluralized_and_lowered_block_types() -> list[str]:
    """Returns a list of the pluralized and lowered block types."""

    return [pluralize_block_type(block_type).lower() for block_type in BlockType]


def pluralize_block_type(block_type: str) -> str:
    """Pluralizes the block type."""

    if block_type == BlockType.CLASS:
        return "classes"
    elif block_type == BlockType.DIRECTORY:
        return "directories"
    else:
        return f"{block_type.lower()}s"


def create_model_from_vertex(vertex_data: dict) -> ModelType:
    """
    Creates a model from the vertex data.

    Args:
        - vertex_data (dict): The vertex data.
    """

    block_type: str | None = vertex_data.get("block_type")

    if block_type == BlockType.MODULE:
        return ModuleModel(**vertex_data)
    elif block_type == BlockType.CLASS:
        return ClassModel(**vertex_data)
    elif block_type == BlockType.FUNCTION:
        return FunctionModel(**vertex_data)
    elif block_type == BlockType.STANDALONE_CODE_BLOCK:
        return StandaloneCodeBlockModel(**vertex_data)
    elif block_type == BlockType.DIRECTORY:
        return DirectoryModel(**vertex_data)
    else:
        raise ValueError(f"Unknown block type: {block_type}")
