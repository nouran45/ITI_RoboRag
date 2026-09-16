import httpx


def check_backend(backend_url: str):
    """Check whether the FastAPI backend is reachable."""

    try:
        response = httpx.get(
            f"{backend_url}/health",
            timeout=3.0,
        )

        response.raise_for_status()

        return True, response.json()

    except Exception:
        return False, None


def query_backend(
    backend_url: str,
    question: str,
):
    """Send a question to the RoboRAG backend."""

    response = httpx.post(
        f"{backend_url}/query",
        json={
            "question": question,
        },
        timeout=120.0,
    )

    response.raise_for_status()

    return response.json()