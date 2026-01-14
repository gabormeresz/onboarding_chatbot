from onboarding_agent.models.config import CHAT_MODEL_NAME, CHAT_TEMPERATURE
from langchain_ollama import ChatOllama


def get_chat_model(tools: list | None = None, num_retries: int = 3):
    """
    Get chat model with optional tool binding and retry logic to handle transient Ollama errors.

    Args:
        tools: Optional list of tools to bind to the model
        num_retries: Number of retries for failed requests (handles NaN errors, timeouts, etc.)
    """
    model = ChatOllama(
        model=CHAT_MODEL_NAME,
        temperature=CHAT_TEMPERATURE,
        num_predict=-1,  # No limit on prediction length
    )

    if tools:
        model = model.bind_tools(tools)

    return model.with_retry(
        stop_after_attempt=num_retries,
        wait_exponential_jitter=True,
    )
