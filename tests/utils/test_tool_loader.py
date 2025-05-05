import pytest
import importlib
import pkgutil
from unittest.mock import MagicMock, patch
from utils.tool_loader import get_enabled_tools_from_config, load_tools_from_package
from interfaces.tool_base import AssistantToolBase


@pytest.fixture
def mock_config_file(tmp_path):
    """Fixture to create a temporary mock configuration file."""
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
    """Test that the function correctly reads enabled tools from the configuration file."""
    with patch(
        "utils.tool_loader.open", lambda path, mode: open(mock_config_file, mode)
    ):
        enabled_tools = get_enabled_tools_from_config()
        assert enabled_tools == [
            "tool1",
            "tool2",
        ], "Should return the enabled tools from config"


def test_get_enabled_tools_from_config_file_not_found():
    """Test that the function returns an empty list when the configuration file is not found."""
    with patch("utils.tool_loader.open", side_effect=FileNotFoundError):
        enabled_tools = get_enabled_tools_from_config()
        assert (
            enabled_tools == []
        ), "Should return an empty list if config file is missing"


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
    """Test that the function loads tools from a package when they are enabled in the configuration."""
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
        assert len(tools) == 1, "Should load one tool from the package"
        assert isinstance(
            tools[0], MockTool
        ), "Loaded tool should be an instance of MockTool"


def test_load_tools_from_package_no_enabled_tools():
    """Test that the function returns an empty list when no tools are enabled in the configuration."""
    mock_package = MagicMock()
    mock_package.__path__ = ["mock_path"]
    mock_package.__name__ = "mock_package"

    with patch("utils.tool_loader.get_enabled_tools_from_config", return_value=[]):
        tools = load_tools_from_package(mock_package)
        assert tools == [], "Should return an empty list if no tools are enabled"
