import os
import requests
from interfaces.tool_base import AssistantToolBase


class CallTeamsAgentTool(AssistantToolBase):
    """
    Classe para transferir a conversa para um agente via Microsoft Teams.
    """

    def __init__(self):
        self.teams_webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
        self.tool_type = "function"
        self.tool_name = "transfer_to_teams_agent"
        self.tool_description = "Detecta quando o usuário deseja falar com um agente via Teams e realiza a transferência."
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A mensagem do usuário solicitando o contato com um agente via Teams",
                }
            },
            "required": ["message"],
        }

    def generate_summary(self, context):
        """
        Gera um resumo das mensagens da conversa utilizando o cliente OpenAI injetado.
        """
        # 1) Recupera histórico de mensagens via threads API e reverte a lista
        msgs = list(
            context.client.beta.threads.messages.list(thread_id=context.thread_id)
        )[::-1]
        formatted = []
        for m in msgs:
            if m.role in ("user"):
                text = ""
                for block in m.content:
                    if block.type == "text" and hasattr(block, "text"):
                        text += block.text.value
                formatted.append({"role": m.role, "content": text})

        if not formatted:
            return "Nenhuma mensagem disponível para resumir."

        # 2) Monta o prompt de system + histórico
        chat_payload = [
            {
                "role": "system",
                "content": "Você é um assistente que resume conversas e extrai somente o que o usuário deseja resolver.",
            },
            {"role": "user", "content": "Resuma a seguinte conversa:"},
        ]
        for entry in formatted:
            chat_payload.append({"role": entry["role"], "content": entry["content"]})

        # 3) Usa O CLIENTE INJETADO para gerar o summary
        resp = context.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID"),
            messages=chat_payload,
            max_tokens=150,  # Limita a quantidade de tokens para resumos curtos
        )

        # 4) Extrai o texto de volta
        return resp.choices[0].message.content.strip()

    def transfer_to_teams_agent(self, user_message: str, conversation_summary: str):

        card_text = f"{conversation_summary}\nVocê pode ajudar?"

        payload = {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": card_text,
                }
            ]
        }

        try:
            r = requests.post(self.teams_webhook_url, json=payload)
            r.raise_for_status()
            print("Mensagem enviada com sucesso para o Teams.")
        except Exception as e:
            print(f"Erro ao enviar para o Teams: {e}")

    def get_tool_infos(self):
        return {
            "type": self.tool_type,
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": self.tool_parameters,
            },
        }

    def execute(self, **kwargs):

        message = kwargs.get("message")
        context = kwargs.get("context")
        if not message:
            raise ValueError("Parâmetro 'message' é obrigatório.")
        if not context:
            raise ValueError("Parâmetro 'context' é obrigatório.")

        # usa o client injetado para gerar o summary
        summary = self.generate_summary(context)

        # envia para o Teams
        self.transfer_to_teams_agent(message, summary)

        return {
            "tool_output": (
                f"Resumo da conversa:\n{summary}\n\n"
                "Mensagem enviada para um agente no Teams."
            )
        }
