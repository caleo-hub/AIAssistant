import pytest
import importlib
import pkgutil
from unittest.mock import MagicMock, patch
from utils.tool_loader import get_enabled_tools_from_config, load_tools_from_package
from interfaces.tool_base import AssistantToolBase


@pytest.fixture
def mock_config_file(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_content = """
    tools:
      enabled:
        - tool1
        - tool2
    """
    config_path.write_text(config_content)
    return config_path


def test_get_enabled_tools_from_config(mock_config_file):
    with patch(
        "utils.tool_loader.open", lambda path, mode: open(mock_config_file, mode)
    ):
        enabled_tools = get_enabled_tools_from_config()
        assert enabled_tools == ["tool1", "tool2"]


def test_get_enabled_tools_from_config_file_not_found():
    with patch("utils.tool_loader.open", side_effect=FileNotFoundError):
        enabled_tools = get_enabled_tools_from_config()
        assert enabled_tools == []


class MockTool(AssistantToolBase):
    def get_tool_infos(self):
        return {
            "type": "function",
            "function": {
                "name": "mock_tool",
                "description": "Mock tool",
                "parameters": {},
            },
        }

    def execute(self, *args, **kwargs):
        return "executed"


def test_load_tools_from_package():
    mock_package = MagicMock()
    mock_package.__path__ = ["mock_path"]
    mock_package.__name__ = "mock_package"

    mock_module = MagicMock()
    mock_module.MockTool = MockTool

    with patch(
        "pkgutil.iter_modules", return_value=[(None, "mock_module", None)]
    ), patch("importlib.import_module", return_value=mock_module), patch(
        "utils.tool_loader.get_enabled_tools_from_config", return_value=["mock_module"]
    ), patch(
        "inspect.getmembers", return_value=[("MockTool", MockTool)]
    ):
        tools = load_tools_from_package(mock_package)
        assert len(tools) == 1
        assert isinstance(tools[0], MockTool)


def test_load_tools_from_package_no_enabled_tools():
    mock_package = MagicMock()
    mock_package.__path__ = ["mock_path"]
    mock_package.__name__ = "mock_package"

    with patch("utils.tool_loader.get_enabled_tools_from_config", return_value=[]):
        tools = load_tools_from_package(mock_package)
        assert tools == []
