# Onboarding Chatbot - Agentic RAG Prototype

## 📋 Project Overview

This project is an **Agentic RAG (Retrieval-Augmented Generation) Chatbot** designed to assist new employees with onboarding tasks. It serves as a prototype for demonstrating the implementation of autonomous agents using **LangGraph**, modular RAG systems, and tool integration.

The chatbot acts as a first line of support for HR and IT queries, capable of answering policy questions using RAG and autonomously escalating critical issues to a ticketing system.

---

## 🎯 Problem Statement

**Domain**: Corporate Onboarding Support (HR & IT)

**Relevance**:
New employees often face information overload and struggle to find specific policies or procedures (e.g., "How do I request a laptop?", "What is the home office policy?"). This leads to repetitive queries for HR and IT departments.

**Solution**:
An intelligent agent that:

1.  **Understands Intent**: Distinguishes between simple questions, complex policy queries, and critical issues.
2.  **Retrieves Knowledge**: Uses a RAG pipeline to answer questions based on internal documentation (Handbooks, Policies).
3.  **Takes Action**: Can autonomously create support tickets for critical issues (e.g., security incidents) or when human intervention is needed.

**Why Agentic RAG?**:
A simple RAG system can only answer questions. An **Agentic** approach allows the system to _decide_ when to answer, when to ask for clarification, and when to perform actions (like raising a ticket), providing a complete resolution workflow rather than just information retrieval.

---

## 🏗️ Architecture

![Architecture Diagram](data/images/RAG%20LLM%20Backend%20Pipeline.png)

The system is built on **LangGraph** and consists of a main agent workflow and a specialized RAG subgraph.

### 1. Main Agent Workflow (LangGraph)

The main graph orchestrates the conversation flow through 6 nodes:

- **`classify_intent`**: Analyzes the user's query to determine the intent (e.g., `policy_query`, `it_support`, `critical_issue`).
- **`router`**: A conditional routing node that directs the flow based on the classification.
- **`response_generation`**: Generates a preliminary response or decides if external knowledge is needed.
- **`rag_call`**: Invokes the RAG subgraph if the agent determines it needs documentation to answer.
- **`escalation`**: Handles critical issues (e.g., "I lost my laptop") by using the **Ticket Tool** to create a support ticket.
- **`final_answer`**: Formats the final response to the user.

### 2. RAG Subgraph

A modular subgraph dedicated to retrieval:

- **`rewrite_query`**: Optimizes the user's query for vector search.
- **`retrieve_docs`**: Fetches relevant chunks from the vector store (ChromaDB).
- **`generate_answer`**: Synthesizes an answer using the retrieved context.

### 3. Tools

- **RAG Tool**: The retrieval subsystem itself acts as a tool for the agent.
- **Ticket Tool**: A functional tool that simulates creating a ticket in an external system (Jira/ServiceNow) for high-priority issues.

---

## 🛠️ Technical Implementation

- **Framework**: [LangGraph](https://langchain-ai.github.io/langgraph/) for agent orchestration.
- **LLM**: **Qwen 2.5 (7B-Instruct)** via [Ollama](https://ollama.com/).
  - _Choice_: Selected for its strong reasoning capabilities and performance-to-size ratio, allowing it to run locally on consumer hardware without API costs.
- **Embeddings**: **BAAI/bge-m3** for high-quality semantic search.
- **Vector Store**: ChromaDB (local).
- **UI**: [Streamlit](https://streamlit.io/) for a clean, interactive chat interface.
- **Containerization**: Fully Dockerized with `docker-compose` for easy reproduction.

---

## 🚀 Installation & Usage

### Prerequisites

- **Docker** & **Docker Compose** installed.
- **Ollama** running locally (or accessible via network) with the `qwen2.5:7b-instruct` model pulled.

### Option 1: Run with Docker (Recommended)

This will start the Chatbot UI and the backend services.

1.  **Clone the repository**:

    ```bash
    git clone <repo-url>
    cd onboarding_chatbot
    ```

2.  **Start the application**:

    ```bash
    docker compose up --build
    ```

3.  **Access the UI**:
    Open your browser at `http://localhost:8501`.

### Option 2: Run Locally

1.  **Install dependencies** (using `uv` or `pip`):

    ```bash
    pip install uv
    uv sync
    ```

2.  **Ingest Knowledge Base**:
    Process the documents in `data/docs/` and build the vector index.

    ```bash
    uv run src/onboarding_agent/rag/ingest.py
    ```

3.  **Run the Streamlit App**:
    ```bash
    PYTHONPATH=src uv run streamlit run streamlit/app.py
    ```

---

## 📊 Evaluation & Performance

### Functional Evaluation

The system includes an automated evaluation framework (`eval/`) testing 18 distinct scenarios, including standard queries, edge cases, and critical escalations.

- **Routing Accuracy**: >85% (Target)
- **Escalation Detection**: Successfully identifies security incidents and creates tickets.

To run the evaluation:

```bash
./eval/run_eval.sh
```

### Load Testing

A load test suite (`loadtest/`) simulates concurrent user traffic to identify bottlenecks.

- **Scenario**: 100 queries with 10 concurrent workers.
- **Typical Latency (Local)**: ~12-18s per query (highly dependent on GPU/CPU).
- **Bottleneck**: The primary bottleneck is **LLM Inference** (Ollama).
- **Optimization**: In a production environment, this would be solved by hosting the LLM on a dedicated inference server (e.g., vLLM) or using a cloud API.

To run the load test:

```bash
./loadtest/run_load_test.sh
```

---

## 📂 Project Structure

```
.
├── data/docs/              # Knowledge base (Markdown files)
├── eval/                   # Evaluation scripts and datasets
├── loadtest/               # Load testing framework
├── src/
│   └── onboarding_agent/
│       ├── agent/          # Main LangGraph workflow
│       ├── rag/            # RAG implementation & Subgraph
│       ├── tools/          # Custom tools (Ticket Tool)
│       └── models/         # LLM & Embedding configuration
├── streamlit/              # UI Application
├── docker-compose.yml      # Container orchestration
└── Dockerfile              # Application container definition
```
