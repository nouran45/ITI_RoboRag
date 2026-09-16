from fastapi import APIRouter, HTTPException, Request

from ...schemas.query import QueryRequest, QueryResponse, SourceItem
from ...core.config import settings
from ...services.generation import GenerationService

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_rag(
    payload: QueryRequest,
    request: Request,
):
    """
    Answer a question using the persisted RoboRAG knowledge base.
    """

    try:
        retrieval_service = request.app.state.retrieval_service
        generation_service = request.app.state.generation_service

        # Retrieve relevant course chunks
        retrieved_chunks = retrieval_service.retrieve(
            payload.question
        )

        if (
            not retrieved_chunks
            or retrieved_chunks[0]["distance"]
            > settings.max_retrieval_distance
        ):
            return QueryResponse(
                answer=GenerationService.FALLBACK_RESPONSE,
                sources=[],
            )

        # Generate grounded answer
        answer = generation_service.generate(
            payload.question,
            retrieved_chunks,
        )

        # Build source list
        sources = []

        seen_sources = set()

        for chunk in retrieved_chunks:
            source_key = (
                chunk["source"],
                chunk["page"],
            )

            if source_key not in seen_sources:
                sources.append(
                    SourceItem(
                        source=chunk["source"],
                        page=chunk["page"],
                        distance=round(
                            chunk["distance"],
                            4,
                        ),
                    )
                )

                seen_sources.add(source_key)

        return QueryResponse(
            answer=answer,
            sources=sources,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(exc)}",
        ) from exc