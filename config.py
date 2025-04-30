import os
from dotenv import load_dotenv

load_dotenv()

AZURE_SEARCH_KEY   = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_SEARCH_EP    = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX = os.getenv("AZURE_AI_SEARCH_INDEX")

# OpenAI vars
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY      = os.getenv("AZURE_OPENAI_KEY")