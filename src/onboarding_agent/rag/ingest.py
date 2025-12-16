"""
RAG ingest pipeline (Markdown only).

- Loads .md documents from data/
- Chunks them
- Creates embeddings using Ollama (bge-m3)
- Persists vectors to Chroma

Run:
  uv run python -m onboarding_agent.rag.ingest
"""

from pathlib import Path
from typing import List
import json

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


# -------- Config --------

DATA_DIR = Path("data/docs")
CHROMA_DIR = Path(".storage/chroma")

EMBEDDING_MODEL = "bge-m3"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# -------- Manifest loading --------

MANIFEST_PATH = Path("data/knowledge_manifest.json")


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("ℹ️ No manifest found, proceeding without metadata enrichment")
        return {}

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return {doc["file"]: doc for doc in raw.get("documents", [])}


# -------- Document loading --------


def load_markdown_documents(data_dir: Path, manifest: dict) -> List:
    documents = []

    for path in data_dir.rglob("*.md"):
        try:
            loader = TextLoader(str(path), encoding="utf-8")
            docs = loader.load()

            # add useful metadata
            manifest_entry = manifest.get(path.name, {})

            for d in docs:
                d.metadata.update(
                    {
                        "source": path.name,
                        "path": str(path),
                        "doc_id": manifest_entry.get("doc_id"),
                        "doc_type": manifest_entry.get("doc_type"),
                    }
                )

            documents.extend(docs)

        except Exception as e:
            print(f"[WARN] Failed to load {path}: {e}")

    return documents


# -------- Ingest pipeline --------


def run_ingest() -> None:
    print("🔹 Starting RAG ingest pipeline (Markdown only)")

    print("📘 Loading knowledge manifest...")
    manifest = load_manifest()

    if not DATA_DIR.exists():
        raise RuntimeError("data/ directory not found")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    print("📄 Loading markdown documents...")
    documents = load_markdown_documents(DATA_DIR, manifest)

    if not documents:
        raise RuntimeError("No markdown documents found in data/")

    print(f"   Loaded {len(documents)} documents")

    print("✂️  Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### "],
    )
    chunks = splitter.split_documents(documents)

    print(f"   Created {len(chunks)} chunks")

    print("🧠 Initializing embeddings...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    print("📦 Writing to Chroma vector store...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    print("✅ Ingest finished successfully")
    print(f"   Vector store persisted at: {CHROMA_DIR.resolve()}")


# -------- Entrypoint --------

if __name__ == "__main__":
    run_ingest()
