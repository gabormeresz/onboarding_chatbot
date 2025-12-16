from onboarding_agent.models.config import CHAT_MODEL_NAME, CHAT_TEMPERATURE
from langchain_ollama import ChatOllama


def get_chat_model():
    return ChatOllama(model=CHAT_MODEL_NAME, temperature=CHAT_TEMPERATURE)
