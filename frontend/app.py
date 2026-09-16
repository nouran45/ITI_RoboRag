import os
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv

from api_client import (
    check_backend,
    query_backend,
)


# =========================================================
# Configuration
# =========================================================

FRONTEND_DIR = Path(__file__).resolve().parent

load_dotenv(FRONTEND_DIR / ".env")

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8010",
)


st.set_page_config(
    page_title="RoboRAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Session state
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# Styling
# =========================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------
       Main application
    -------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(0, 174, 239, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at top left,
                rgba(100, 80, 255, 0.08),
                transparent 25%
            ),
            #070b14;

        color: #e6edf7;
    }


    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }


    /* --------------------------------------------------
       Sidebar
    -------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: #0b111d;
        border-right: 1px solid #1c293b;
    }


    [data-testid="stSidebar"] * {
        color: #dce7f5;
    }


    /* --------------------------------------------------
       Hero
    -------------------------------------------------- */

    .robot-hero {
        padding: 30px 32px;
        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(13, 27, 48, 0.97),
                rgba(8, 15, 28, 0.97)
            );

        border: 1px solid #22354d;

        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.28);

        margin-bottom: 28px;
    }


    .rag-badge {
        display: inline-block;

        padding: 5px 11px;
        margin-bottom: 14px;

        border-radius: 20px;

        background: rgba(64, 186, 255, 0.10);

        border:
            1px solid rgba(64, 186, 255, 0.30);

        color: #77d5ff;

        font-size: 0.78rem;
        font-weight: 700;
    }


    .robot-title {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;

        background:
            linear-gradient(
                90deg,
                #66d9ff,
                #8ba7ff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }


    .robot-subtitle {
        color: #9fb0c7;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 12px;
        margin-bottom: 0;
        max-width: 820px;
    }


    /* --------------------------------------------------
       Topic cards
    -------------------------------------------------- */

    .topic-card {
        background: #0d1522;

        border: 1px solid #1e2d42;

        border-radius: 13px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
            0 6px 20px rgba(0, 0, 0, 0.12);
    }


    .topic-title {
        font-weight: 700;
        color: #dce9f7;
        font-size: 1rem;
        margin-bottom: 9px;
    }


    .topic-description {
        color: #8fa2b8;
        font-size: 0.90rem;
        line-height: 1.55;
    }


    /* --------------------------------------------------
       Chat
    -------------------------------------------------- */

    [data-testid="stChatMessage"] {
        background: #0d1420;

        border: 1px solid #1d2a3d;

        border-radius: 14px;

        padding: 8px;

        margin-bottom: 14px;
    }


    [data-testid="stChatInput"] {
        border: 1px solid #26394f;
        border-radius: 14px;
    }


    /* --------------------------------------------------
       Buttons
    -------------------------------------------------- */

    .stButton > button {
        width: 100%;

        border-radius: 10px;

        background: #101c2d;

        border: 1px solid #273b54;

        color: #d5e5f5;

        transition: 0.15s ease;
    }


    .stButton > button:hover {
        border-color: #51c8ff;
        color: #79d7ff;
        background: #132238;
    }


    /* --------------------------------------------------
       Expanders
    -------------------------------------------------- */

    [data-testid="stExpander"] {
        background: #0b1320;
        border: 1px solid #213149;
        border-radius: 12px;
    }


    /* Hide Streamlit footer */
    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Helper functions
# =========================================================

@st.cache_data(ttl=10)
def check_backend():
    """
    Check whether the FastAPI backend is reachable.
    """

    try:
        response = httpx.get(
            f"{BACKEND_URL}/health",
            timeout=3.0,
        )

        response.raise_for_status()

        return True, response.json()

    except Exception:
        return False, None


def query_backend(question: str):
    """
    Send a question to the FastAPI RAG backend.
    """

    response = httpx.post(
        f"{BACKEND_URL}/query",
        json={
            "question": question,
        },
        timeout=120.0,
    )

    response.raise_for_status()

    return response.json()


def render_sources(sources):
    """
    Render source citations using native Streamlit components.
    """

    if not sources:
        return

    with st.expander(
        f"📚 Sources ({len(sources)})",
        expanded=False,
    ):

        for source in sources:

            with st.container(border=True):

                col1, col2 = st.columns(
                    [4, 1],
                    vertical_alignment="center",
                )

                with col1:
                    st.markdown(
                        f"**📄 {source['source']}**"
                    )

                with col2:
                    st.markdown(
                        f"**Page {source['page']}**"
                    )


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.markdown("## 🤖 RoboRAG")

    st.caption(
        "Robotics Course Intelligence"
    )

    st.divider()

    st.markdown("### About")

    st.write(
        """
        **RoboRAG** is a retrieval-augmented
        study assistant built around the indexed
        **CSE 432 Robotics** course lectures.
        """
    )

    st.write(
        """
        Instead of answering from general internet
        knowledge, the assistant retrieves relevant
        lecture material and generates answers based
        on that evidence.
        """
    )

    st.divider()

    st.markdown("### 📘 Knowledge Areas")

    st.markdown(
        """
        - Introduction to Robotics
        - Rigid Motion
        - 3D Rotation
        - Forward Kinematics
        - Velocity Kinematics
        - Jacobians
        - Robot Singularities
        - Mobile Robots
        """
    )

    st.divider()

    st.markdown("### ⚙️ System Status")

    backend_online, health_data = check_backend()

    if backend_online:

        st.success(
            "RAG backend online"
        )

        if health_data:
            st.caption(
                f"{health_data.get('app', 'RoboRAG API')} "
                f"v{health_data.get('version', '')}"
            )

    else:

        st.error(
            "Backend offline"
        )

        st.caption(
            "Start the FastAPI backend "
            "before asking questions."
        )

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# Hero
# =========================================================

st.html(
    """
    <div class="robot-hero">

        <div class="rag-badge">
            RETRIEVAL-AUGMENTED ROBOTICS ASSISTANT
        </div>

        <div class="robot-title">
            RoboRAG
        </div>

        <p class="robot-subtitle">
            Your AI study companion for robotics.
            Ask questions about course concepts and receive
            explanations grounded in the indexed lecture material,
            together with document and page citations.
        </p>

    </div>
    """
)


# =========================================================
# Topic summary
# =========================================================

st.markdown(
    "### What can I help you study?"
)

col1, col2, col3 = st.columns(3)


with col1:

    st.html(
        """
        <div class="topic-card">

            <div class="topic-title">
                🦾 Robot Kinematics
            </div>

            <div class="topic-description">
                Study forward kinematics,
                coordinate frames, rigid motion,
                transformations and rotations.
            </div>

        </div>
        """
    )


with col2:

    st.html(
        """
        <div class="topic-card">

            <div class="topic-title">
                ⚙️ Motion Analysis
            </div>

            <div class="topic-description">
                Explore velocity kinematics,
                Jacobians, robot motion analysis
                and singularities.
            </div>

        </div>
        """
    )


with col3:

    st.html(
        """
        <div class="topic-card">

            <div class="topic-title">
                🤖 Mobile Robotics
            </div>

            <div class="topic-description">
                Learn about locomotion mechanisms
                and mobile robot movement concepts.
            </div>

        </div>
        """
    )


# =========================================================
# Example questions
# =========================================================

st.markdown("### Try an example")

example_questions = [
    "What is forward kinematics?",
    "How does the Jacobian relate to robot motion?",
    "What happens near a robot singularity?",
    "What types of mobile robot locomotion are covered?",
]


example_columns = st.columns(2)

selected_question = None


for i, example in enumerate(
    example_questions
):

    with example_columns[i % 2]:

        if st.button(
            example,
            key=f"example_{i}",
            use_container_width=True,
        ):

            selected_question = example


st.divider()


# =========================================================
# Conversation history
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        if message["role"] == "assistant":

            st.caption(
                "📘 Grounded answer from the "
                "robotics knowledge base"
            )

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            render_sources(
                message["sources"]
            )


# =========================================================
# Chat input
# =========================================================

typed_question = st.chat_input(
    "Ask about robotics, kinematics, Jacobians, singularities..."
)


if selected_question:

    question = selected_question

else:

    question = typed_question


# =========================================================
# Process question
# =========================================================

if question:

    # -----------------------------------------------------
    # Store user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # -----------------------------------------------------
    # Assistant response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        st.caption(
            "📘 Grounded answer from the "
            "robotics knowledge base"
        )

        with st.spinner(
            "Searching the robotics knowledge base..."
        ):

            try:

                data = query_backend(
                    question
                )

                answer = data.get(
                    "answer",
                    "No answer was returned.",
                )

                sources = data.get(
                    "sources",
                    [],
                )


                st.markdown(answer)

                render_sources(
                    sources
                )


                # -----------------------------------------
                # Save assistant response
                # -----------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )


            except httpx.ConnectError:

                error_message = (
                    "I cannot reach the RoboRAG backend. "
                    "Please make sure the FastAPI server "
                    "is running."
                )

                st.error(error_message)


            except httpx.TimeoutException:

                error_message = (
                    "The model took too long to respond. "
                    "Please try again."
                )

                st.error(error_message)


            except httpx.HTTPStatusError as exc:

                error_message = (
                    "The backend returned an error "
                    f"({exc.response.status_code})."
                )

                st.error(error_message)


            except Exception as exc:

                error_message = (
                    f"Unexpected error: {exc}"
                )

                st.error(error_message)