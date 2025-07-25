import os
from interfaces.tool_base import AssistantToolBase
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class AISearchTool(AssistantToolBase):
    """
    Classe para realizar buscas vetorizadas no Azure Cognitive Search.

    Baseada no seu esquema de índice, ela retorna:
      - IDs do chunk e do documento
      - Título
      - Trecho de texto (até 300 chars)
      - Caminhos de conteúdo e metadados
      - Informações de arquivo (nome, tipo, data de criação, idioma, etc.)
      - Dados de localização (página e bounding polygons)
      - Score de relevância
    """

    def __init__(self):
        self.vector_field = "content_embedding"

        self.api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
        self.endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        self.index_name = os.getenv("AZURE_AI_SEARCH_INDEX")

        self.credential = self._create_credential()
        self.client = self._create_search_client()

        # metadados da ferramenta para registro em get_tool_infos()
        self.tool_type = "function"
        self.tool_name = "ai_search_tool"
        self.tool_description = "Data source para RAG do chatbot"
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto a ser pesquisado pelo RAG",
                },
                "search_needed": {
                    "type": "boolean",
                    "description": "Se deve ou não executar a busca vetorizada",
                },
                "k_results": {
                    "type": "integer",
                    "description": "Número de resultados a retornar",
                },
            },
            "required": ["query", "search_needed"],
        }

    def _create_credential(self):
        if not self.api_key:
            raise ValueError("AZURE_AI_SEARCH_API_KEY não configurada.")
        return AzureKeyCredential(self.api_key)

    def _create_search_client(self):
        if not self.endpoint or not self.index_name:
            raise ValueError(
                "AZURE_AI_SEARCH_ENDPOINT ou AZURE_AI_SEARCH_INDEX não configurados."
            )
        return SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential,
        )

    def ai_search_tool(self, **kwargs):
        """
        Executa a busca vetorizada e retorna o output processado + citações.
        """
        query = kwargs.get("query", "")
        k_results = kwargs.get("k_results", 3)
        search_needed = kwargs.get("search_needed", True)

        if not search_needed:
            return {"tool_output": None, "citations": []}

        # 🔍 busca vetorizada (text-as-vector)
        results = self.client.search(
            vector_queries=[
                {
                    "kind": "text",
                    "text": query,
                    "fields": self.vector_field,
                    "k": k_results,
                }
            ],
            top=k_results,
            select=[
                # IDs e títulos
                "content_id",
                "text_document_id",
                "document_title",
                # Texto e caminhos
                "content_text",
                "content_path",
                # Metadados de armazenamento
                "metadata_storage_path",
                "metadata_storage_name",
                "metadata_storage_content_type",
                "metadata_language",
                "metadata_title",
                "metadata_creation_date",
                # Localização dentro do documento
                "locationMetadata/pageNumber",
                "locationMetadata/boundingPolygons",
            ],
        )

        processed = self._process_results(results)
        return {
            "tool_output": processed,
            "citations": self._format_citation(processed),
        }

    def _process_results(self, results):
        """
        Constrói uma lista de dicts com TODOS os campos que importam.
        """
        output = []
        for r in results:
            # r é um SearchResult — pode ter .score ou '@search.score'
            score = getattr(r, "score", r.get("@search.score", None))
            loc = r.get("locationMetadata", {}) or {}
            output.append({
                "content_id":               r.get("content_id"),
                "text_document_id":         r.get("text_document_id"),
                "title":                    r.get("document_title"),
                "chunk":                    (r.get("content_text") or "")[:300],
                "content_path":             r.get("content_path"),
                "metadata_storage_path":    r.get("metadata_storage_path"),
                "metadata_storage_name":    r.get("metadata_storage_name"),
                "metadata_storage_type":    r.get("metadata_storage_content_type"),
                "metadata_language":        r.get("metadata_language"),
                "metadata_title":           r.get("metadata_title"),
                "metadata_creation_date":   r.get("metadata_creation_date"),
                "page_number":              loc.get("pageNumber"),
                "bounding_polygons":        loc.get("boundingPolygons"),
                "score":                    score,
            })
        return output

    def _format_citation(self, results):
        """
        Gera uma lista de citações simples para o RAG.
        """
        citations = []
        for idx, r in enumerate(results, start=1):
            citations.append({
                "id":       idx,
                "filename": r["metadata_storage_name"] or r["title"],
                "url":      r["metadata_storage_path"],
                "score":    r["score"],
            })
        return citations

    def get_tool_infos(self):
        return {
            "type": self.tool_type,
            "function": {
                "name":        self.tool_name,
                "description": self.tool_description,
                "parameters":  self.tool_parameters,
            },
        }

    def execute(self, **kwargs):
        """
        Ponto de entrada único para a ferramenta.
        """
        # garante query obrigatória
        if not kwargs.get("query"):
            raise ValueError("O parâmetro 'query' é obrigatório.")
        return self.ai_search_tool(**kwargs)
