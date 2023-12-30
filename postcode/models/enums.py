from enum import Enum


class ImportModuleType(str, Enum):
    """Enum of import module types."""

    STANDARD_LIBRARY = "STANDARD_LIBRARY"
    LOCAL = "LOCAL"
    THIRD_PARTY = "THIRD_PARTY"

    def __str__(self) -> str:
        return self.value


class CommentType(str, Enum):
    """Class representing the different types of important comments."""

    TODO = "TODO"
    FIXME = "FIXME"
    NOTE = "NOTE"
    HACK = "HACK"
    XXX = "XXX"
    REVIEW = "REVIEW"
    OPTIMIZE = "OPTIMIZE"
    CHANGED = "CHANGED"
    QUESTION = "QUESTION"
    Q = "Q"
    DEPRECATED = "@deprecated"
    NOSONAR = "NOSONAR"
    TODO_FIXME = "TODO-FIXME"

    def __str__(self) -> str:
        return self.value


class BlockType(str, Enum):
    """Enum of code block types."""

    STANDALONE_CODE_BLOCK = "STANDALONE_BLOCK"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    MODULE = "MODULE"
    DIRECTORY = "DIRECTORY"

    def __str__(self) -> str:
        return self.value
