import ollama

from ..core.config import settings


class GenerationService:

    FALLBACK_RESPONSE = (
        "I could not find this information in the provided "
        "robotics course documents."
    )

    def build_context(
        self,
        retrieved_chunks: list[dict],
    ) -> str:
        """
        Format retrieved chunks for the LLM.
        """

        context_blocks = []

        for chunk in retrieved_chunks:
            context_blocks.append(
                f"[Source: {chunk['source']}, "
                f"Page: {chunk['page']}]\n"
                f"{chunk['text']}"
            )

        return "\n\n".join(context_blocks)


    def generate(
        self,
        question: str,
        retrieved_chunks: list[dict],
    ) -> str:
        """
        Generate a useful but strictly grounded study answer.
        """

        context = self.build_context(
            retrieved_chunks
        )

        system_message = """
You are RoboRAG, a university robotics course assistant.

Your ONLY factual source is the retrieved robotics course context.

Your goal is to explain the concept clearly enough for a student
to study it, while remaining strictly grounded in the retrieved material.

ANSWER STYLE

For conceptual questions:

1. Start with a direct definition or answer.

2. Then explain additional relevant information found in the context.

3. When supported by the context, explain:
   - how the concept relates to another concept,
   - why it is important,
   - its properties,
   - or its consequences.

4. Normally write 3-6 informative sentences.

5. Use two short paragraphs or bullet points when useful.

6. Do not repeat the same definition several times using different wording.

STRICT GROUNDING

7. Every technical statement must be supported by the retrieved context.

8. You may paraphrase and combine facts from multiple retrieved chunks.

9. Do NOT add examples unless the examples explicitly appear in the context.

10. Do NOT add applications, tasks, robot components, equations,
    formulas, or terminology unless explicitly supported by the context.

11. Do NOT use general pretrained robotics knowledge to make
    the answer sound more complete.

12. Never invent information merely to make the answer longer.

13. If the retrieved material supports only a short explanation,
    give a short explanation.

14. Do not begin with fragments such as "The Jacobian."
    Begin with a complete sentence.

15. If the context genuinely does not contain enough information,
    reply exactly:

"I could not find this information in the provided robotics course documents."

16. If the retrieved context clearly contains the answer,
    do not refuse.
"""

        user_message = f"""
QUESTION:
{question}

RETRIEVED ROBOTICS COURSE CONTEXT:
{context}

Write a clear study explanation using only information supported
by the retrieved context.
"""

        response = ollama.chat(
            model=settings.ollama_model,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            options={
                "temperature": 0,
                "num_predict": 350,
            },
        )

        answer = (
            response["message"]["content"]
            .strip()
        )

        # Retry only when retrieval is clearly relevant
        # but the model incorrectly refuses.
        if (
            answer == self.FALLBACK_RESPONSE
            and retrieved_chunks
            and retrieved_chunks[0]["distance"] <= 0.50
        ):

            retry_message = f"""
The retrieved context is strongly relevant to the student's question.

QUESTION:
{question}

CONTEXT:
{context}

Your previous response incorrectly refused to answer.

Read the context carefully and answer using ONLY facts supported
by the retrieved course material.

Give a clear explanation of about 3-6 sentences if the context
contains enough information.

Do not add outside knowledge, examples, applications, or equations.
"""

            retry_response = ollama.chat(
                model=settings.ollama_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": retry_message,
                    },
                ],
                options={
                    "temperature": 0,
                    "num_predict": 350,
                },
            )

            answer = (
                retry_response[
                    "message"
                ]["content"]
                .strip()
            )

        return answer