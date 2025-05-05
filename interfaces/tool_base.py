from abc import ABC, abstractmethod


class AssistantToolBase(ABC):
    @abstractmethod
    def get_tool_infos(self):
        """
        This method should return information about the tool, such as its name, description, and usage.
        """
        pass

    @abstractmethod
    def execute(self, context, **kwargs):
        """
        This method should define the functionality of the tool when it is executed.
        """
        pass
