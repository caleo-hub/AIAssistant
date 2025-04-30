from utils.tool_loader import load_tools_from_package
from services import tools as tools_package
from openai import AzureOpenAI
import os
import ast


class Assistant:
    """
    A class to manage the integration with Azure OpenAI and dynamically loaded tools.
    This class initializes an Azure OpenAI client, loads tools dynamically, and creates
    an assistant instance with the specified configuration. It also provides functionality
    to call tools by their names.
    Attributes:
        client (AzureOpenAI): The Azure OpenAI client instance.
        deployment (str): The deployment ID for the Azure OpenAI model.
        role_prompt (str): The role prompt instructions for the assistant.
        tool_instances (list): A list of dynamically loaded tool instances.
        tools_schemas (list): A list of tool schemas in OpenAI format.
        assistant (object): The assistant instance created using the Azure OpenAI client.
        tool_map (dict): A mapping of tool function names to their respective instances.
    """

    def __init__(self):
        self.client = self._initialize_client()
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")
        self.role_prompt = os.getenv("ROLE_PROMPT")
        self.tool_instances = self._load_tools()
        self.tools_schemas = self._extract_tool_schemas()
        self.assistant = self._create_assistant()
        self.tool_map = self._map_tools()

    def _initialize_client(self):
        """Inicializa o cliente Azure OpenAI."""
        return AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

    def _load_tools(self):
        """Carrega ferramentas dinamicamente do pacote."""
        return load_tools_from_package(tools_package)

    def _extract_tool_schemas(self):
        """Extrai os schemas das ferramentas em formato OpenAI."""
        return [tool.get_tool_infos() for tool in self.tool_instances]

    def _create_assistant(self):
        """Cria o assistente com as ferramentas declaradas e configurações adicionais."""

        return self.client.beta.assistants.create(
            model=self.deployment,
            instructions=self.role_prompt,
            tools=self.tools_schemas,
            temperature=1,
            top_p=1,
        )

    def _map_tools(self):
        """Cria o mapeamento de nome da função para instância da classe."""
        return {
            tool.get_tool_infos()["function"]["name"]: tool
            for tool in self.tool_instances
        }

    def call_tool_by_name(self, name, arguments: str):
        """Chama uma ferramenta pelo nome."""

        # Converte a string de um dicionário para um dicionário real
        try:
            arguments = ast.literal_eval(arguments)
            if not isinstance(arguments, dict):
                raise ValueError(
                    "Os argumentos fornecidos não são um dicionário válido."
                )
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Erro ao processar os argumentos: {e}")

        tool = self.tool_map.get(name)
        if not tool:
            raise ValueError(f"Ferramenta '{name}' não encontrada.")
        return tool.execute(**arguments)
