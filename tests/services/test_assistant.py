import pytest
from unittest.mock import MagicMock, patch
from services.assistant import Assistant


@pytest.fixture
def mock_environment_variables(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_ID", "test_deployment")
    monkeypatch.setenv("ROLE_PROMPT", "You are a helpful assistant.")


@pytest.fixture
def assistant_instance(mock_environment_variables):
    with patch("services.assistant.load_tools_from_package") as mock_load_tools, patch(
        "services.assistant.AzureOpenAI"
    ) as mock_azure_openai:
        mock_tool = MagicMock()
        mock_tool.get_tool_infos.return_value = {
            "function": {"name": "mock_tool_function"}
        }
        mock_load_tools.return_value = [mock_tool]
        mock_azure_openai.return_value.beta.assistants.create.return_value = MagicMock()
        return Assistant()


def test_initialize_client(mock_environment_variables):
    with patch("services.assistant.AzureOpenAI") as mock_azure_openai:
        assistant = Assistant()
        mock_azure_openai.assert_called_once_with(
            azure_endpoint="https://example.com",
            api_key="test_api_key",
            api_version="2023-03-15-preview",
        )


def test_load_tools(assistant_instance):
    assert len(assistant_instance.tool_instances) == 1
    assert (
        assistant_instance.tool_instances[0].get_tool_infos()["function"]["name"]
        == "mock_tool_function"
    )


def test_extract_tool_schemas(assistant_instance):
    assert len(assistant_instance.tools_schemas) == 1
    assert (
        assistant_instance.tools_schemas[0]["function"]["name"] == "mock_tool_function"
    )


def test_create_assistant(assistant_instance):
    assert assistant_instance.assistant is not None


def test_map_tools(assistant_instance):
    assert "mock_tool_function" in assistant_instance.tool_map


def test_call_tool_by_name_success(assistant_instance):
    mock_tool = assistant_instance.tool_map["mock_tool_function"]
    mock_tool.execute.return_value = "success"
    result = assistant_instance.call_tool_by_name(
        "mock_tool_function", '{"arg1": "value1"}'
    )
    mock_tool.execute.assert_called_once_with(arg1="value1")
    assert result == "success"


def test_call_tool_by_name_invalid_arguments(assistant_instance):
    with pytest.raises(ValueError, match="Erro ao processar os argumentos"):
        assistant_instance.call_tool_by_name("mock_tool_function", "invalid_json")


def test_call_tool_by_name_tool_not_found(assistant_instance):
    with pytest.raises(
        ValueError, match="Ferramenta 'non_existent_tool' não encontrada."
    ):
        assistant_instance.call_tool_by_name("non_existent_tool", '{"arg1": "value1"}')
