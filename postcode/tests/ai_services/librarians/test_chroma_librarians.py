# TODO: Complete tests for ChromaLibrarian

import json
from typing import Any, Generator
import pytest
from unittest.mock import patch, MagicMock

from postcode.ai_services.librarians.chroma_librarians import ChromaLibrarian
from postcode.databases.chroma.chromadb_collection_manager import (
    ChromaCollectionManager,
)

import postcode.types.chroma as chroma_types


@pytest.fixture
def mock_openai_client() -> Generator[MagicMock, Any, None]:
    with patch("openai.OpenAI") as mock_openai:
        yield mock_openai()


@pytest.fixture
def mock_chroma_collection_manager() -> Generator[MagicMock, Any, None]:
    with patch(
        "postcode.databases.chroma.chromadb_collection_manager.ChromaCollectionManager"
    ) as mock_manager:
        yield mock_manager()


def test_query_chroma(
    mock_chroma_collection_manager: MagicMock, mock_openai_client: MagicMock
) -> None:
    librarian = ChromaLibrarian(mock_chroma_collection_manager)

    mock_openai_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps({"query_list": ["query1", "query2", "query3"]})
                )
            )
        ]
    )

    mock_chroma_collection_manager.query_collection.return_value = MagicMock()

    result: chroma_types.QueryResult | None = librarian.query_chroma("user_question")

    assert result is not None
    assert mock_chroma_collection_manager.query_collection.called
