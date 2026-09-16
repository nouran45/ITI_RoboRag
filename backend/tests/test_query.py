from fastapi.testclient import TestClient

from backend.app.main import app


class MockRetrievalService:
    def retrieve(self, question: str, top_k=None):
        return [
            {
                "rank": 1,
                "text": "The Jacobian is a matrix used in robot motion analysis.",
                "source": "07_velocity_kinematics.pdf",
                "page": 2,
                "chunk_index": 0,
                "distance": 0.2787,
            }
        ]


class MockGenerationService:
    def generate(self, question: str, retrieved_chunks: list[dict]):
        return "The Jacobian is a matrix used in robot motion analysis."


# Use mocks so tests do not need to load Chroma, MiniLM, or Ollama.
app.state.retrieval_service = MockRetrievalService()
app.state.generation_service = MockGenerationService()

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "RoboRAG API"


def test_query_success():
    response = client.post(
        "/query",
        json={
            "question": "What is the Jacobian in robotics?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data

    assert (
        data["answer"]
        == "The Jacobian is a matrix used in robot motion analysis."
    )

    assert len(data["sources"]) == 1

    assert (
        data["sources"][0]["source"]
        == "07_velocity_kinematics.pdf"
    )

    assert data["sources"][0]["page"] == 2


def test_empty_question_returns_422():
    response = client.post(
        "/query",
        json={
            "question": ""
        },
    )

    assert response.status_code == 422