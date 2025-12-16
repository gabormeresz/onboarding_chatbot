from onboarding_agent.models.config import EMBEDDING_MODEL_NAME
from langchain_ollama import OllamaEmbeddings


def get_embedding_model():
    return OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
