import json

import chromadb
from sentence_transformers import SentenceTransformer

from ..core.config import settings


class RetrievalService:
    def __init__(self):
        # Load saved RAG configuration
        with open(settings.rag_config_path, "r", encoding="utf-8") as f:
            self.rag_config = json.load(f)

        # Load embedding model once
        self.embedding_model = SentenceTransformer(
            self.rag_config["embedding_model"],
            device="cpu",
        )

        # Load persistent ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(settings.vector_store_path)
        )

        self.collection = self.client.get_collection(
            name=self.rag_config["collection_name"]
        )

    def embed_query(self, question: str) -> list[float]:
        """
        Convert the user question into an embedding vector.
        """
        embedding = self.embedding_model.encode(
            [question],
            normalize_embeddings=True,
        )[0]

        return embedding.tolist()

    def normalize_query(self, question: str) -> str:
        """
        Make short or vague user questions more explicit for
        semantic retrieval while preserving the original question
        for answer generation.
        """

        question = " ".join(question.strip().split())

        lower_question = question.lower()

        definition_starters = (
            "what is",
            "what are",
            "define",
            "explain",
        )

        if lower_question.startswith(definition_starters):
            return (
                "Robotics course concept definition and explanation: "
                f"{question}"
            )

        return f"Robotics course question: {question}"

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks from ChromaDB.
        """

        if top_k is None:
            top_k = settings.top_k

        retrieval_query = self.normalize_query(question)

        query_embedding = self.embed_query(
            retrieval_query
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved_chunks = []

        for rank, (document, metadata, distance) in enumerate(
            zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ),
            start=1,
        ):
            retrieved_chunks.append(
                {
                    "rank": rank,
                    "text": document,
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_index": metadata["chunk_index"],
                    "distance": float(distance),
                }
            )

        return retrieved_chunks