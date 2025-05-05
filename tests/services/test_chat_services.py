import unittest
import pytest
from unittest.mock import MagicMock, patch
from services.chat_services import ChatServices

@pytest.fixture
def chat_services():
    with patch("services.chat_services.Assistant") as MockAssistant, \
         patch("services.chat_services.AISearchTool") as MockAISearchTool:
        mock_assistant_instance = MockAssistant.return_value
        mock_client = MagicMock()
        mock_assistant_instance.client = mock_client
        mock_assistant_instance.assistant = MagicMock()
        mock_search_tool = MockAISearchTool.return_value

        chat_service = ChatServices()
        chat_service.assistant_instance = mock_assistant_instance
        chat_service.client = mock_client
        chat_service.search_tool = mock_search_tool
        yield chat_service

def test_create_new_thread(chat_services):
    mock_thread = MagicMock()
    mock_thread.id = "test_thread_id"
    chat_services.client.beta.threads.create.return_value = mock_thread

    thread_id = chat_services.create_new_thread()

    assert thread_id == "test_thread_id"
    chat_services.client.beta.threads.create.assert_called_once()

def test_retrieve_old_thread(chat_services):
    thread_id = "existing_thread_id"

    chat_services.retrieve_old_thread(thread_id)

    chat_services.client.beta.threads.retrieve.assert_called_once_with(thread_id=thread_id)

def test_add_user_message(chat_services):
    chat_services.thread_id = "test_thread_id"
    user_message = "Hello, this is a test message."

    chat_services.add_user_message(user_message)

    chat_services.client.beta.threads.messages.create.assert_called_once_with(
        thread_id="test_thread_id", role="user", content=user_message
    )

def test_execute_assistant_completed(chat_services):
    chat_services.thread_id = "test_thread_id"
    mock_run = MagicMock()
    mock_run.status = "completed"
    chat_services.client.beta.threads.runs.create.return_value = mock_run
    chat_services.client.beta.threads.runs.retrieve.return_value = mock_run
    mock_message = MagicMock()
    mock_message.role = "assistant"
    mock_message.content = [MagicMock(type="text", text=MagicMock(value="Test response"))]
    chat_services.client.beta.threads.messages.list.return_value = [mock_message]

    answer, citations = chat_services.execute_assistant()

    assert answer == "Test response"
    assert citations == []
    chat_services.client.beta.threads.runs.create.assert_called_once_with(
        thread_id="test_thread_id",
        additional_instructions=unittest.mock.ANY,
        assistant_id=chat_services.assistant.id,
        tool_choice="required",
    )
    chat_services.client.beta.threads.messages.list.assert_called()

def test_execute_assistant_requires_action(chat_services):
    chat_services.thread_id = "test_thread_id"
    mock_run = MagicMock()
    mock_run.status = "requires_action"
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "ai_search_tool"
    mock_tool_call.function.arguments = {"query": "test"}
    mock_run.required_action.submit_tool_outputs.tool_calls = [mock_tool_call]
    chat_services.client.beta.threads.runs.create.return_value = mock_run
    chat_services.client.beta.threads.runs.retrieve.return_value = mock_run
    chat_services.assistant_instance.call_tool_by_name.return_value = {
        "tool_output": "Tool output",
        "citations": [{"id": 1, "filename": "doc1", "url": "http://example.com/doc1"}],
    }

    answer, citations = chat_services.execute_assistant()

    assert citations == [{"id": 1, "filename": "doc1", "url": "http://example.com/doc1"}]
    chat_services.assistant_instance.call_tool_by_name.assert_called_once_with(
        name="ai_search_tool", arguments={"query": "test"}
    )
    chat_services.client.beta.threads.runs.submit_tool_outputs_and_poll.assert_called()