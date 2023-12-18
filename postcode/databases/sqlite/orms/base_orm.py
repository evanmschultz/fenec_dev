from datetime import datetime
from typing import Literal

from sqlalchemy import Connection, event
from sqlmodel import (
    Field,
    SQLModel,
    Column,
    String,
    Integer,
    ForeignKey,
    select,
    union_all,
)
from sqlalchemy.sql.expression import Subquery

from postcode.python_parser.models import (
    BlockType,
    CommentModel,
    DependencyModel,
    ImportModel,
)


class BaseCodeBlockORM(SQLModel, table=False):
    id: str = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    block_type: Literal[
        BlockType.STANDALONE_CODE_BLOCK,
        BlockType.CLASS,
        BlockType.FUNCTION,
        BlockType.MODULE,
    ]
    start_line_num: int
    end_line_num: int
    code_content: str = ""
    important_comments: list[str] | None = None
    # # Parent_id is required if the block-type is not MODULE
    # parent_id: str | None = Field(default=None, foreign_key="basecodeblockorm.id")

    def set_important_comments(self, comments: list[CommentModel]) -> None:
        """Serialize the list of CommentModel objects to a JSON string."""
        self.important_comments = (
            [comment.model_dump_json() for comment in comments] if comments else None
        )

    def get_important_comments(self) -> list[CommentModel] | None:
        """Get important comments, parsing the JSON string back into CommentModel objects."""
        return (
            [CommentModel.model_validate_json(item) for item in self.important_comments]
            if self.important_comments
            else None
        )


@event.listens_for(BaseCodeBlockORM, "before_update")
def receive_before_update(connection: Connection, target: BaseCodeBlockORM) -> None:
    """Update the updated_at field before updating the row."""
    target.updated_at = datetime.utcnow()


class Modules(BaseCodeBlockORM, table=True):
    __tablename__: str = "modules"

    imports: list[str] = Field(sa_column=Column(String, default=""))
    module_imports: list[int] = Field(
        sa_column=Column(Integer, ForeignKey("modules.id"))
    )
    class_imports: list[int] = Field(
        sa_column=Column(Integer, ForeignKey("classes.id"))
    )
    function_imports: list[int] = Field(
        sa_column=Column(Integer, ForeignKey("functions.id"))
    )
    standalone_code_block_imports: list[int] = Field(
        sa_column=Column(Integer, ForeignKey("standalone_code_blocks.id"))
    )

    def set_imports(self, imports: list[ImportModel]) -> None:
        """Serialize the list of ImportModel objects to a JSON string."""
        self.imports = [import_.model_dump_json() for import_ in imports]

    def get_imports(self) -> list[ImportModel] | None:
        """Get imports, parsing the JSON string back into ImportModel objects."""
        return (
            [ImportModel.model_validate_json(item) for item in self.imports]
            if self.imports
            else None
        )

    # dependencies = Relationship("DependencyModel", back_populates="base_code_block")
    # children = relationship("ChildModel", back_populates="parent")

    # dependencies: list[
    #     ImportModel | DependencyModel
    # ] | None = None  # this is supposed to be a list of relationships to other tables that inherit from BaseCodeBlockORM if the import model is of ImportModuleType.LOCAL, otherwise it holds the model of the import
    # summary: str = ""
    # children: list = (
    #     []
    # )  # this is supposed to be list of relationships to other tables that inherit from BaseCodeBlockORM


class Classes(BaseCodeBlockORM, table=True):
    __tablename__: str = "classes"


class Functions(BaseCodeBlockORM, table=True):
    __tablename__: str = "functions"


class StandaloneCodeBlocks(BaseCodeBlockORM, table=True):
    __tablename__: str = "standalone_code_blocks"


# Create a polymorphic union
polymorphic_union: Subquery = union_all(
    select([Modules.__table__]),
    select([Classes.__table__]),
    select([Functions.__table__]),
    select([StandaloneCodeBlocks.__table__]),
).alias("polymorphic_union")

# Use this union in relationships
BaseCodeBlockORM.__table__ = BaseCodeBlockORM.__table__.join(
    polymorphic_union, BaseCodeBlockORM.id == polymorphic_union.c.id
)
