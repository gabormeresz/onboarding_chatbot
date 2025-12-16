from langchain_chroma import Chroma
from onboarding_agent.models.embeddings import get_embedding_model
from pathlib import Path

PERSIST_DIR = "data/chroma"


def get_vectorstore():
    return Chroma(
        persist_directory=str(Path(PERSIST_DIR)),
        embedding_function=get_embedding_model(),
    )
