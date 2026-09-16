🤖 RoboRAG — Robotics Course Document Assistant

A full-stack Retrieval-Augmented Generation (RAG) application that helps students study robotics course material by asking natural-language questions and receiving grounded answers with document and page citations.

RoboRAG retrieves semantically relevant lecture chunks from a persisted ChromaDB vector store, generates answers locally with Llama 3.2 through Ollama, exposes the pipeline through a FastAPI backend, and serves it through a dark, robotics-themed Streamlit chat interface.

The project is designed as a Core Track text-based RAG assistant for robotics lecture PDFs.

Table of Contents

Features

Architecture

Tech Stack

Project Structure

Knowledge Base

RAG Configuration

Vector Store Schema

Getting Started

Backend Setup

Frontend Setup

API Reference

How Retrieval Works

RAG Evaluation

Testing

Docker

Environment Variables

Screenshots

Known Limitations

Future Improvements

Contributors

License

Features

Semantic search across robotics lecture PDFs

Retrieval-Augmented Generation using a local LLM

Fully local inference through Ollama

Sentence-transformer embeddings using sentence-transformers/all-MiniLM-L6-v2

Persistent ChromaDB vector store

No vector-store rebuilding during normal API requests

Source-aware answers with exact PDF filenames and page numbers

FastAPI REST backend with typed Pydantic request/response schemas

Streamlit chat interface with a professional dark robotics theme

Source expanders showing the documents used for each answer

Query normalization for short or vague robotics questions

Retrieval-distance filtering for clearly out-of-domain questions

Prompt grounding with refusal behavior for unsupported questions

Embedding model and vector store loaded once at FastAPI startup

Frontend/backend communication configured through environment variables

Automated backend tests for health, happy-path query, and invalid input

Pinned backend and frontend requirements

Dockerfile for the backend service

Architecture

                         ┌──────────────────────┐
                         │         User         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Streamlit Frontend  │
                         │ Chat + Sources + UX  │
                         └──────────┬───────────┘
                                    │
                              POST /query
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Backend    │
                         └──────────┬───────────┘
                                    │
                           normalize question
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ SentenceTransformer  │
                         │ all-MiniLM-L6-v2     │
                         └──────────┬───────────┘
                                    │ query embedding
                                    ▼
                         ┌──────────────────────┐
                         │      ChromaDB        │
                         │ Top-K cosine search  │
                         └──────────┬───────────┘
                                    │ retrieved chunks
                                    ▼
                         ┌──────────────────────┐
                         │  Grounded Context    │
                         │ text + source + page │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Ollama + Llama 3.2   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Answer + Sources    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                           Streamlit Chat UI

End-to-end RAG flow

Question
→ Query Normalization
→ Query Embedding
→ ChromaDB Retrieval
→ Top-4 Context Chunks
→ Grounded Ollama Generation
→ Answer + PDF/Page Sources

Tech Stack

Component

Technology

Language

Python 3.11

LLM

Llama 3.2

Local LLM Runtime

Ollama

Embeddings

SentenceTransformers

Embedding Model

sentence-transformers/all-MiniLM-L6-v2

Embedding Dimension

384

Vector Database

ChromaDB

Retrieval Metric

Cosine distance

Backend

FastAPI

Validation

Pydantic / Pydantic Settings

Frontend

Streamlit

HTTP Client

HTTPX

Configuration

python-dotenv / .env

Testing

Pytest + FastAPI TestClient

Containerization

Docker

Project Structure

ITI_RoboRag/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── query.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── schemas/
│   │   │   └── query.py
│   │   ├── services/
│   │   │   ├── generation.py
│   │   │   └── retrieval.py
│   │   ├── utils/
│   │   │   └── logging_config.py
│   │   └── main.py
│   │
│   ├── data/
│   │   ├── rag_config.json
│   │   ├── final_evaluation.csv
│   │   └── vector_store/
│   │       ├── chroma.sqlite3
│   │       └── ...
│   │
│   ├── tests/
│   │   └── test_query.py
│   │
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── .env.example
│   ├── requirements.txt
│   └── .streamlit/
│       └── config.toml
│
├── notebooks/
│   └── rag_pipeline.ipynb
│
├── screenshots/
│   ├── 01_roborag_home.png
│   ├── 02_grounded_answer.png
│   ├── 03_out_of_domain_refusal.png
│   ├── 04_fastapi_docs.png
│   └── 05_*.png
│
├── data/
│   └── raw/                        # source PDFs; may be excluded from Git
│
├── .dockerignore
├── .gitignore
└── README.md



Knowledge Base

RoboRAG is built around 11 robotics lecture PDFs from the CSE 432 Robotics course.



The indexed lecture topics include:

Introduction to Robotics

Rigid Motion

3D Rotation

Forward Kinematics

Velocity Kinematics

Jacobians

Robot Singularities

Mobile Robots

The source PDFs are parsed with pypdf, lightly cleaned, split into overlapping chunks, embedded, and stored in ChromaDB.

RAG Configuration

{
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "collection_name": "roborag_chunks",
  "chunk_size": 800,
  "chunk_overlap": 150,
  "embedding_dimension": 384,
  "number_of_documents": 11,
  "number_of_chunks": 422,
  "top_k": 4,
  "ollama_model": "llama3.2:latest",
  "max_retrieval_distance": 0.65
}

Stored at:

backend/data/rag_config.json

Chunking strategy

RoboRAG uses page-aware fixed-size chunking:

Chunk size: 800 characters

Overlap: 150 characters

The overlap preserves context across chunk boundaries, while source/page metadata supports exact citations.

Vector Store Schema

RoboRAG uses ChromaDB as the persisted vector database.

Field

Description

id

Unique chunk identifier such as source_pX_cY

document

Chunk text

embedding

384-dimensional MiniLM embedding

metadata.source

Source PDF filename

metadata.page

Original PDF page number

metadata.chunk_index

Chunk index

Collection name:

roborag_chunks

The backend loads the persisted vector store at startup; it does not rebuild the knowledge base for each request.

Getting Started

1. Prerequisites

Install:

Python 3.10+

Git

Ollama

Verify:

python --version
git --version
ollama --version

2. Clone the repository

git clone https://github.com/nouran45/ITI_RoboRag.git
cd ITI_RoboRag

3. Create a virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

4. Set up Ollama

ollama pull llama3.2

If Ollama is not already running:

ollama serve

Backend Setup

From the repository root:

cd backend
pip install -r requirements.txt

Create a local .env.

Windows

Copy-Item .env.example .env

macOS / Linux

cp .env.example .env

Example:

APP_NAME=RoboRAG API
APP_VERSION=1.0.0

TOP_K=4
OLLAMA_MODEL=llama3.2:latest
MAX_RETRIEVAL_DISTANCE=0.65

CORS_ORIGINS=http://localhost:8501

Start the backend from the repository root:

python -m uvicorn backend.app.main:app --port 8000

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

Frontend Setup

Open a second terminal:

cd frontend
pip install -r requirements.txt

Create frontend/.env.

Windows

Copy-Item .env.example .env

macOS / Linux

cp .env.example .env

Example:

BACKEND_URL=http://127.0.0.1:8000

Run:

streamlit run app.py

Open:

http://localhost:8501

API Reference

Health Check

GET /health

Example:

{
  "status": "ok",
  "app": "RoboRAG API",
  "version": "1.0.0"
}

Ask a Question

POST /query

Request:

{
  "question": "What is the Jacobian in robotics?"
}

Example response:

{
  "answer": "The Jacobian in robotics is a matrix that ...",
  "sources": [
    {
      "source": "07_velocity_kinematics.pdf",
      "page": 2,
      "distance": 0.3195
    }
  ]
}

Empty input returns HTTP 422.

cURL example

curl -X POST "http://127.0.0.1:8000/query"   -H "Content-Type: application/json"   -d "{\"question\":\"What is the Jacobian in robotics?\"}"

How Retrieval Works

The question is lightly normalized for robotics-domain semantic retrieval.

all-MiniLM-L6-v2 creates a 384-dimensional query embedding.

ChromaDB performs cosine-distance semantic search.

The backend retrieves the Top-4 most relevant chunks.

A retrieval-distance threshold helps reject clearly unrelated questions.

Retrieved text is combined with source/page metadata.

The grounded context is sent to Llama 3.2 through Ollama.

FastAPI returns the answer plus PDF/page citations.

Streamlit displays the result.

RAG Evaluation

The final system was manually evaluated using 12 questions:

10 supported robotics questions

2 deliberately unsupported questions

Final metrics

Metric

Result

Supported retrieval success

100.0%

Supported answer accuracy

100.0%

Overall answer accuracy

100.0%

Fully grounded answer rate

91.7%

Unsupported-question refusal rate

100.0%

These percentages describe this manually reviewed 12-question evaluation set; they are not a universal benchmark.

Evaluation questions

#

Question

Retrieval

Answer

Grounding

1

What is the Jacobian in robotics?

✅

✅

✅

2

What is a robot singularity?

✅

✅

✅

3

What is forward kinematics?

✅

✅

Mostly

4

What is a rotation matrix?

✅

✅

✅

5

How are rotations represented in three dimensions?

✅

✅

✅

6

What is velocity kinematics?

✅

✅

✅

7

What is the relationship between joint velocities and robot motion?

✅

✅

✅

8

What are the different types of mobile robot locomotion?

✅

✅

✅

9

Why is the Jacobian important in robot motion?

✅

✅

✅

10

What problems can occur near a robot singularity?

✅

✅

✅

11

What was Microsoft's revenue in 2025?

N/A

✅ Refused

✅

12

What is the capital city of Australia?

N/A

✅ Refused

✅

Full evaluation artifact:

backend/data/final_evaluation.csv

Failure analysis

Retrieval returned relevant robotics material for all supported evaluation questions.

The main limitation appeared in generation grounding: one forward-kinematics response was rated mostly grounded because it included some explanatory terminology beyond the exact retrieved wording, while the core answer remained correct.

Mitigations used during development included:

Top-K tuning

query normalization

a retrieval-distance threshold

temperature 0

grounded prompt instructions

evaluation with supported and unsupported questions

Testing

Backend tests:

backend/tests/test_query.py

They cover:

GET /health

successful POST /query

empty-question validation returning HTTP 422

Run:

python -m pytest backend/tests -v

Expected:

3 passed

Docker

Backend Dockerfile:

backend/Dockerfile

Build from repository root:

docker build -f backend/Dockerfile -t roborag-backend .

Example:

docker run -p 8000:8000 roborag-backend

Ollama is a separate runtime. The container must be able to reach the Ollama service on the host or another container.

Environment Variables

Backend

Variable

Example

Description

APP_NAME

RoboRAG API

API application name

APP_VERSION

1.0.0

Application version

TOP_K

4

Number of retrieved chunks

OLLAMA_MODEL

llama3.2:latest

Ollama generation model

MAX_RETRIEVAL_DISTANCE

0.65

Retrieval-distance cutoff

CORS_ORIGINS

http://localhost:8501

Allowed frontend origin

Frontend

Variable

Example

Description

BACKEND_URL

http://127.0.0.1:8000

FastAPI base URL

Never commit real .env files.

Screenshots

RoboRAG Home



Grounded Robotics Answer



Out-of-Domain Refusal



FastAPI Swagger Documentation



Additional Application View



Update the fifth filename if needed.

Known Limitations

Answer quality depends on the indexed lecture content.

A local LLM may occasionally introduce minor explanatory wording beyond the retrieved text.

Semantic retrieval can miss information when source extraction is poor or phrasing differs greatly from lecture terminology.

The assistant currently indexes a fixed robotics corpus.

Conversation-aware follow-up retrieval is not yet implemented.

Ollama must be available locally.

Future Improvements

Retrieval reranking

Hybrid keyword + semantic retrieval

Evidence extraction before generation

Conversation-aware follow-up questions

Direct PDF uploads and automatic indexing

Expanded robotics knowledge base

Automated RAG evaluation metrics

Richer citation previews

Docker Compose for frontend + backend + Ollama

Optional multimodal robotics diagram support

Contributors

Nouran Yasser Salama

[Second team member name]

Replace the placeholder before submission.

License

This project is intended for educational use.

If institutional lecture material is used as the knowledge base, ensure it is used and distributed according to the applicable institutional policies.

Summary

Robotics PDFs
      ↓
Parsing + Cleaning
      ↓
800-character Chunks
      ↓
MiniLM Embeddings
      ↓
Persistent ChromaDB
      ↓
Top-4 Semantic Retrieval
      ↓
Grounded Llama 3.2 Generation
      ↓
FastAPI
      ↓
Streamlit
      ↓
Answer + PDF/Page Sources

RoboRAG demonstrates a complete local RAG product: raw robotics documents are transformed into a searchable vector knowledge base, served through an API, and exposed through an interactive study assistant with traceable citations.
