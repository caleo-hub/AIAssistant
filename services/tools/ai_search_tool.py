import os
from interfaces.tool_base import AssistantToolBase
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class AISearchTool(AssistantToolBase):
    """
    Classe para realizar buscas vetorizadas no Azure Cognitive Search.

    Esta classe utiliza as melhores práticas para autenticação e execução de buscas
    vetorizadas em um índice configurado no Azure Cognitive Search. Ela é projetada
    para ser usada como uma ferramenta auxiliar em assistentes baseados em IA.
    """

    def __init__(self):
        """
        Inicializa a classe AISearchTool carregando variáveis de ambiente,
        configurando o cliente de busca e definindo o campo vetorial.
        """
        self.campo_vetorial = "text_vector"  # Nome do campo vetorizado no índice

        self.api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
        self.endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        self.ai_search_index = os.getenv("AZURE_AI_SEARCH_INDEX")

        self.credential = self._create_credential()
        self.client = self._create_search_client()

        # Variáveis do dicionário get_tool_infos
        self.tool_type = "function"
        self.tool_name = "ai_search_tool"
        self.tool_description = "Data source para RAG do chatbot"
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A exato solicitação/query do usuário no chat para o Retrieval Augmented Generation",
                },
                "search_needed": {
                    "type": "boolean",
                    "description": "Avalia se aquery do usuário precisa de um Retrieval Augmented Generation ou não precisa",
                },
            },
            "required": ["query", "search_needed"],
        }

    def _create_credential(self):
        """
        Cria e retorna as credenciais para autenticação no Azure Cognitive Search.

        :return: Instância de AzureKeyCredential.
        """
        if not self.api_key:
            raise ValueError("AZURE_AI_SEARCH_API_KEY não configurada.")
        return AzureKeyCredential(self.api_key)

    def _create_search_client(self):
        """
        Cria e retorna o cliente de busca para o Azure Cognitive Search.

        :return: Instância de SearchClient.
        """
        if not self.endpoint or not self.ai_search_index:
            raise ValueError(
                "AZURE_AI_SEARCH_ENDPOINT ou AZURE_AI_SEARCH_INDEX não configurados."
            )
        return SearchClient(
            endpoint=self.endpoint,
            index_name=self.ai_search_index,
            credential=self.credential,
        )

    def ai_search_tool(self, **kwargs):
        """
        Realiza uma busca vetorizada no índice configurado no Azure Cognitive Search.

        :param kwargs: Parâmetros opcionais, incluindo:
            - query (str): Texto a ser pesquisado.
            - k_results (int): Número de resultados a serem retornados (padrão: 3).
        :return: Lista de tuplas contendo os resultados no formato:
            (chunk, title, metadata_storage_path).
        """
        search_needed = kwargs.get("search_needed", True)
        query = kwargs.get("query", "")
        k_results = kwargs.get("k_results", 3)

        if not search_needed:
            return {
                "tool_output": None,
                "citations": [],
            }

        # 🔍 Realiza a busca vetorizada
        results = self.client.search(
            vector_queries=[
                {
                    "kind": "text",
                    "text": query,
                    "fields": self.campo_vetorial,
                    "k": k_results,
                }
            ],
            top=k_results,
            select=[
                "chunk",
                "title",
                "metadata_storage_path",
            ],  # Campos que deseja retornar
        )

        # 📦 Processa os resultados
        processed_results = self._process_results(results)
        return {
            "tool_output": processed_results,
            "citations": self._format_citation(processed_results),
        }

    def _format_citation(self, results):
        citations = []
        for i, result in enumerate(results, start=1):
            citations.append(
                {
                    "id": i,
                    "filename": result.get("title", "Sem Título"),
                    "url": result.get("metadata_storage_path", "Sem Link"),
                    "score": result.get("score", "Sem score"),
                }
            )
        return citations

    def _process_results(self, results):
        """
        Processa os resultados da busca e os formata como uma lista de tuplas.

        :param results: Resultados retornados pelo cliente de busca.
        :return: Lista de tuplas no formato (chunk, title, metadata_storage_path).
        """
        processed_results = [
            {
                "chunk": result.get("chunk", "")[
                    :300
                ],  # Limita o chunk a 300 caracteres
                "title": result.get("title", "sem título"),
                "metadata_storage_path": result.get(
                    "metadata_storage_path", "sem nome"
                ),
                "score": result.get(
                    "@search.score", 0
                ),  # Adiciona o score de relevância
            }
            for result in results
        ]
        return processed_results

    def get_tool_infos(self):
        """
        Retorna as informações da ferramenta, incluindo o tipo e os parâmetros esperados.

        :return: Dicionário com as informações da ferramenta.
        """
        return {
            "type": self.tool_type,
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": self.tool_parameters,
            },
        }

    def execute(self, query: str, k_results: int = 3, search_needed: bool = True):
        """
        Executa a busca vetorizada com os parâmetros fornecidos.

        :param prompt: Texto a ser pesquisado.
        :param k_results: Número de resultados a serem retornados (padrão: 3).
        :return: Resultados da busca no formato de lista de tuplas.
        """
        return self.ai_search_tool(
            query=query, k_results=k_results, search_needed=search_needed
        )
