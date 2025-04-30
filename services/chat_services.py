# import logging
# from services.assistant import Assistant
# from services.tools.ai_search_tool import AISearchTool  # ajuste o path conforme seu projeto


# class ChatServices:
#     def __init__(self):
#         # inicializa o assistente e o cliente OpenAI
#         self.assistant_instance = Assistant()
#         self.client = self.assistant_instance.client
#         self.assistant = self.assistant_instance.assistant
#         # inicializa ferramenta de busca vetorizada
#         self.search_tool = AISearchTool()
        
#     def create_new_thread(self):
#         logging.info("Criando nova thread.")
#         thread = self.client.beta.threads.create()
#         self.thread_id = thread.id  
#         return self.thread_id
    
#     def retrieve_old_thread(self, thread_id):
#         logging.info(f"Recuperando thread existente: {thread_id}")
#         self.client.beta.threads.retrieve(thread_id=thread_id)
    
#     def make_RAG(self, prompt):
#         docs = self.search_tool.ai_search_documents(prompt=prompt, k_results=3)
#         formatted = []
#         self.citations = []
#         for i, (chunk, title, path) in enumerate(docs, start=1):
#             formatted.append(
#                 f"Documento {i}:\n"
#                 f"- Título: {title}\n"
#                 f"- Fonte: {path}\n"
#                 f"- Trecho: {chunk}\n"
#             )
#             self.citations.append(
#                 {
#                     "id": i,
#                     "filename": title,
#                     "url": path,
#                 }
#             )
#         context_str = (
#             "Contexto Recuperado (RAG):\n\n"
#             + "\n".join(formatted)
#             + "\nUse este contexto para responder à pergunta do usuário."
#         )

#         # injeta o contexto como mensagem de system
#         self.client.beta.threads.messages.create(
#             thread_id=self.thread_id,
#             role="assistant",
#             content=context_str
#         )

#         # envia a mensagem original do usuário
#         self.client.beta.threads.messages.create(
#             thread_id=self.thread_id,
#             role="user",
#             content=prompt
#         )
    
#     def execute_assistant(self):
#         logging.info("Executando assistente.")
#         run = self.client.beta.threads.runs.create(
#             thread_id=self.thread_id,
#             assistant_id=self.assistant.id
#         )

#         # espera até completar
#         while run.status in ["queued", "in_progress", "cancelling"]:
#             logging.debug(f"Status do run: {run.status}. Aguardando...")
#             run = self.client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)

#         # coleta a resposta final
#         answer = ""
#         if run.status == "completed":
#             messages = list(
#                 self.client.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id)
#             )
#             assistant_message = next(
#                 (m for m in reversed(messages) if m.role == "assistant"), None
#             )
#             if assistant_message:
#                 # concatena todos os blocos de texto
#                 for block in assistant_message.content:
#                     if block.type == "text" and hasattr(block, "text"):
#                         answer += block.text.value
                        
#         elif run.status == "requires_action":
#             tool_outputs = []
#             for tool in run.required_action.submit_tool_outputs.tool_calls:
#                 tool_return = self.assistant_instance.call_tool_by_name(name = tool.function.name,
#                                                           arguments = tool.function.arguments)
#                 tool_output = {
#                     "tool_call_id": tool.id,
#                     "output": tool_return
#                 }
#                 tool_outputs.append(tool_output)
#             try:
#                 run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
#                     thread_id=self.thread_id,
#                     run_id=run.id,
#                     tool_outputs=tool_outputs
#                 )
#                 logging.info("Tool outputs submitted successfully.")
#             except Exception as e:
#                 logging.error("Failed to submit tool outputs:", e)
        
#         messages = list(
#             self.client.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id)
#         )
#         assistant_message = next(
#             (m for m in reversed(messages) if m.role == "assistant"), None
#         )
#         if assistant_message:
#             # concatena todos os blocos de texto
#             for block in assistant_message.content:
#                 if block.type == "text" and hasattr(block, "text"):
#                     answer += block.text.value
                        
#         return answer, self.citations

import logging
from services.assistant import Assistant
from services.tools.ai_search_tool import AISearchTool  # ajuste o path conforme seu projeto


class ChatServices:
    def __init__(self):
        # inicializa o assistente e o cliente OpenAI
        self.assistant_instance = Assistant()
        self.client = self.assistant_instance.client
        self.assistant = self.assistant_instance.assistant
        # inicializa ferramenta de busca vetorizada
        self.search_tool = AISearchTool()
        
    def create_new_thread(self):
        logging.info("Criando nova thread.")
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id  
        return self.thread_id
    
    def retrieve_old_thread(self, thread_id):
        logging.info(f"Recuperando thread existente: {thread_id}")
        self.client.beta.threads.retrieve(thread_id=thread_id)
        
    def add_user_message(self, content: str):
        """
        Adiciona uma mensagem do usuário ao thread atual.
        """
        logging.info(f"Adicionando mensagem do usuário ao thread: {content!r}")
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=content
        )
    
    def execute_assistant(self):
        logging.info("Executando assistente.")
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            additional_instructions=(
            "Você é um assistente técnico especializado em fornecer respostas precisas "
            "e bem estruturadas. Sempre utilize o contexto recuperado via RAG para fundamentar suas respostas, "
            "cite as fontes recuperadas (use números entre colchetes para indicar citações) "
            "e formate tudo em Markdown (títulos, listas, blocos de código, etc.). "
            "Caso não encontre informações relevantes, diga apenas: Desculpe, não consegui encontrar informações relevantes para sua pergunta. "
            ),

            assistant_id=self.assistant.id,
            tool_choice="required"
        )

        # espera até completar
        while run.status in ["queued", "in_progress", "cancelling"]:
            logging.debug(f"Status do run: {run.status}. Aguardando...")
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)

        # coleta a resposta final
        answer = ""
        if run.status == "completed":
            messages = list(
                self.client.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id)
            )
            assistant_message = next(
                (m for m in reversed(messages) if m.role == "assistant"), None
            )
            if assistant_message:
                # concatena todos os blocos de texto
                for block in assistant_message.content:
                    if block.type == "text" and hasattr(block, "text"):
                        answer += block.text.value
                        
        elif run.status == "requires_action":
            tool_outputs = []
            self.citations = []
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                tool_return = self.assistant_instance.call_tool_by_name(name = tool.function.name,
                                                          arguments = tool.function.arguments)
                logging.info(f"Function Name {tool.function.name}\nArguments:{tool.function.arguments}")
                if tool.function.name == "ai_search_tool":
                    for i, (_, title, path) in enumerate(tool_return, start=1):
                        self.citations.append(
                            {
                                "id": i,
                                "filename": title,
                                "url": path,
                            }
                        )
                tool_output = {
                    "tool_call_id": tool.id,
                    "output": str(tool_return)
                }
                tool_outputs.append(tool_output)
            try:
                run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=self.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                logging.info("Tool outputs submitted successfully.")
            except Exception as e:
                logging.error("Failed to submit tool outputs:", e)
        
        messages = list(
            self.client.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id)
        )
        assistant_message = next(
            (m for m in reversed(messages) if m.role == "assistant"), None
        )
        if assistant_message:
            # concatena todos os blocos de texto
            for block in assistant_message.content:
                if block.type == "text" and hasattr(block, "text"):
                    answer += block.text.value
                        
        return answer, self.citations

