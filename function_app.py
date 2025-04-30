import os
import logging
import json
import time

from dotenv import load_dotenv
import azure.functions as func

from services.chat_services import ChatServices

# carrega variáveis de ambiente
load_dotenv()

# inicializa o FunctionApp
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

chat_services = ChatServices()




@app.route(route="chatbotapi")
def chatbotapi(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Recebida requisição em /chatbotapi")

    # parse do body
    try:
        req_body = req.get_json()
        logging.debug(f"Request body: {req_body}")
    except ValueError:
        logging.error("JSON inválido no corpo da requisição.")
        return func.HttpResponse("Invalid JSON", status_code=400)

    role = req_body.get("role")
    content = req_body.get("content")
    thread_id = req_body.get("threadId")

    if not role or not content:
        logging.error("Faltando 'role' ou 'content' na requisição.")
        return func.HttpResponse("Fields 'role' and 'content' are required.", status_code=400)

    try:
        # obtém ou cria a thread
        if not thread_id:
            thread_id = chat_services.create_new_thread()
        else:
            chat_services.retrieve_old_thread(thread_id)

        chat_services.add_user_message(content=content)
        answer, citations = chat_services.execute_assistant()
        
        # monta e retorna o HTTP response
        response_body = {
            "threadId": thread_id,
            "answer": answer,
            "citations": citations
        }
        return func.HttpResponse(
            json.dumps(response_body),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Erro interno: {e}", exc_info=True)
        return func.HttpResponse(
            "An internal error occurred. Please try again later.",
            status_code=500
        )
