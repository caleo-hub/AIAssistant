import os
from interfaces.tool_base import AssistantToolBase
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class AISearchTool(AssistantToolBase):
    """
    Classe para buscas vetorizadas no Azure Cognitive Search,
    retornando content_text, document_title e url, e
    construindo url a partir de blob endpoint se metadata_storage_path for None.
    """

    def __init__(self):
        self.vector_field     = "content_embedding"
        self.api_key          = os.getenv("AZURE_AI_SEARCH_API_KEY")
        self.endpoint         = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        self.index_name       = os.getenv("AZURE_AI_SEARCH_INDEX")
        self.blob_endpoint    = os.getenv("SEARCH_AI_BLOB_ENDPOINT")

        if not self.api_key:
            raise ValueError("AZURE_AI_SEARCH_API_KEY não configurada.")
        if not (self.endpoint and self.index_name):
            raise ValueError("AZURE_AI_SEARCH_ENDPOINT ou AZURE_AI_SEARCH_INDEX não configurados.")
        if not self.blob_endpoint:
            raise ValueError("SEARCH_AI_BLOB_ENDPOINT não configurado.")
        
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

        self.credential = AzureKeyCredential(self.api_key)
        self.client     = SearchClient(
            endpoint   = self.endpoint,
            index_name = self.index_name,
            credential = self.credential,
        )

    def ai_search_tool(self, **kwargs):
        """
        Parâmetros (via kwargs):
          - query         (str): texto a ser pesquisado
          - search_needed (bool): roda ou não a busca
          - k_results     (int): número de resultados (default 3)
          - ignora outros kwargs (ex: context)
        Retorna:
          {"tool_output": [...], "citations": [...]}
        """
        query         = kwargs.get("query", "")
        search_needed = kwargs.get("search_needed", True)
        k_results     = kwargs.get("k_results", 3)

        if not search_needed:
            return {"tool_output": [], "citations": []}

        results = self.client.search(
            vector_queries=[{
                "kind":   "text",
                "text":   query,
                "fields": self.vector_field,
                "k":      k_results,
            }],
            top=k_results,
            select=[
                "content_text",
                "document_title",
                "metadata_storage_path",
            ],
        )

        processed = self._process_results(results)
        citations = self._format_citation(processed)
        return {"tool_output": processed, "citations": citations}

    def _process_results(self, results):
        """
        Constrói lista de dicts com content_text, document_title e url,
        criando url via blob_endpoint se metadata_storage_path for None.
        """
        processed = []
        for r in results:
            title = r.get("document_title") or ""
            raw_url = r.get("metadata_storage_path")
            if raw_url:
                url = raw_url
            else:
                # garante exatamente uma barra entre endpoint e título
                url = f"{self.blob_endpoint.rstrip('/')}/{title.lstrip('/')}"
            processed.append({
                "content_text":   (r.get("content_text") or "")[:300],
                "document_title": title,
                "url":            url,
            })
        return processed

    def _format_citation(self, items):
        """
        Gera citações simples a partir do título e da URL, sem repetições.
        """
        citations = []
        seen = set()
        for item in items:
            key = (item["document_title"] or "Sem título", item["url"])
            if key not in seen:
                seen.add(key)
                citations.append({
                    "id":       len(citations) + 1,
                    "filename": key[0],
                    "url":      key[1],
                })
        return citations

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

    def execute(self, **kwargs):
        """
        Ponto de entrada: garante que 'query' seja fornecida.
        """
        if not kwargs.get("query"):
            raise ValueError("O parâmetro 'query' é obrigatório.")
        return self.ai_search_tool(**kwargs)
