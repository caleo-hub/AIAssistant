import os
import pytest
from unittest.mock import MagicMock, patch
from services.tools.ai_search_tool import AISearchTool


@pytest.fixture
def mock_env_vars():
    with patch.dict(
        os.environ,
        {
            "AZURE_AI_SEARCH_API_KEY": "fake_api_key",
            "AZURE_AI_SEARCH_ENDPOINT": "https://fake-endpoint.search.windows.net",
            "AZURE_AI_SEARCH_INDEX": "fake_index",
        },
    ):
        yield


@pytest.fixture
def mock_search_client():
    with patch("services.tools.ai_search_tool.SearchClient") as MockSearchClient:
        mock_client = MagicMock()
        MockSearchClient.return_value = mock_client
        yield mock_client


def test_aisearchtool_initialization(mock_env_vars, mock_search_client):
    tool = AISearchTool()
    assert tool.api_key == "fake_api_key"
    assert tool.endpoint == "https://fake-endpoint.search.windows.net"
    assert tool.ai_search_index == "fake_index"
    assert tool.client == mock_search_client


def test_search_documents(mock_env_vars, mock_search_client):
    mock_search_client.search.return_value = [
        {
            "chunk": "This is a test chunk.",
            "title": "Test Title",
            "metadata_storage_path": "test/path",
        }
    ]
    tool = AISearchTool()
    results = tool.execute(query="test query", k_results=1, search_needed=True)

    assert len(results['tool_output']) == 1
    assert results["tool_output"][0] == {'chunk': 'This is a test chunk.', 'title': 'Test Title', 'metadata_storage_path': 'test/path', 'score': 0}
    assert results["citations"][0] == {'id': 1, 'filename': 'Test Title', 'url': 'test/path', 'score': 0}
    mock_search_client.search.assert_called_once_with(
        vector_queries=[
            {"kind": "text", "text": "test query", "fields": "text_vector", "k": 1}
        ],
        top=1,
        select=["chunk", "title", "metadata_storage_path"],
    )
