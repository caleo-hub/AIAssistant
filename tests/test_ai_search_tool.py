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
    results = tool.ai_search_documents(prompt="test prompt", k_results=1)

    assert len(results) == 1
    assert results[0] == ("This is a test chunk.", "Test Title", "test/path")
    mock_search_client.search.assert_called_once_with(
        vector_queries=[
            {"kind": "text", "text": "test prompt", "fields": "text_vector", "k": 1}
        ],
        top=1,
        select=["chunk", "title", "metadata_storage_path"],
    )


def test_get_tool_infos(mock_env_vars):
    tool = AISearchTool()
    tool_infos = tool.get_tool_infos()

    assert tool_infos["type"] == "function"
    assert tool_infos["function"]["name"] == "ai_search_documents"
    assert "description" in tool_infos["function"]
    assert "parameters" in tool_infos["function"]


def test_execute(mock_env_vars, mock_search_client):
    mock_search_client.search.return_value = [
        {
            "chunk": "This is a test chunk.",
            "title": "Test Title",
            "metadata_storage_path": "test/path",
        }
    ]
    tool = AISearchTool()
    results = tool.execute(prompt="test prompt", k_results=1)

    assert len(results) == 1
    assert results[0] == ("This is a test chunk.", "Test Title", "test/path")
