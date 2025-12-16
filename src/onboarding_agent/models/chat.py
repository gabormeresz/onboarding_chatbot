from onboarding_agent.models.config import CHAT_MODEL_NAME, CHAT_TEMPERATURE
from langchain_ollama import ChatOllama


def get_chat_model(num_retries: int = 3):
    """
    Get chat model with retry logic to handle transient Ollama errors.
    
    Args:
        num_retries: Number of retries for failed requests (handles NaN errors, timeouts, etc.)
    """
    return ChatOllama(
        model=CHAT_MODEL_NAME,
        temperature=CHAT_TEMPERATURE,
        num_predict=-1,  # No limit on prediction length
    ).with_retry(
        stop_after_attempt=num_retries,
        wait_exponential_jitter=True,
    )
