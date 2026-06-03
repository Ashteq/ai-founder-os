"""
hiring_assist.py — AI Founder OS  |  Module 3: Hiring Assistant
Accepts high-level job goals/descriptions, cross-references vector history for
cultural notes and tool configs, then synthesizes a structured candidate
scorecard matrix and technical interview rubrics.
"""

from typing import List, Dict
import ollama
import database
import meeting_intel  # reuse embed_text


# ---------------------------------------------------------------------------
# Context retrieval
# ---------------------------------------------------------------------------

def retrieve_hiring_context(job_description: str, top_k: int = 5) -> List[Dict]:
    """
    Pull the top-k semantically relevant chunks from founder_knowledge that
    relate to the job description — looking for cultural notes, values,
    tool mentions, team dynamics, and past hiring discussions.

    Args:
        job_description: Raw job goals or role description string
        top_k:           Number of context chunks to retrieve

    Returns:
        List of row dicts from database.query_vector_similarity
    """
    if not job_description.strip():
        return []

    query_embedding = meeting_intel.embed_text(job_description)
    context_chunks = database.query_vector_similarity(
        query_vector=query_embedding,
        limit=top_k,
    )
    return context_chunks


# ---------------------------------------------------------------------------
# Scorecard & rubric generation
# ---------------------------------------------------------------------------

def generate_hiring_package(
    role_title: str,
    job_description: str,
    context_chunks: List[Dict],
    model: str = "qwen3:latest",
) -> str:
    """
    Generate a complete hiring package using Ollama:
    - Candidate scorecard matrix (weighted criteria)
    - Technical interview rubric
    - Culture-fit signal questions derived from knowledge base

    Args:
        role_title:      Short role name (e.g. "Senior Backend Engineer")
        job_description: Full high-level job goals and requirements
        context_chunks:  Retrieved cultural and historical context from vector DB
        model:           Ollama model for generation

    Returns:
        Markdown string containing the full hiring package
    """
    # Format retrieved context
    context_text = ""
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("module_source", "unknown")
            title = chunk.get("document_title", "untitled")
            text = chunk.get("text_chunk", "")
            dist = chunk.get("distance", 0)
            context_parts.append(
                f"[Context {i} | source: {source} | doc: {title} | relevance: {1 - float(dist):.2f}]\n{text}"
            )
        context_text = "\n\n".join(context_parts)
    else:
        context_text = "No historical company context available."

    prompt = f"""You are a world-class Head of Talent and Chief-of-Staff for a high-growth startup.
Your job is to create a rigorous, founder-aligned hiring package.

ROLE: {role_title}

JOB GOALS & DESCRIPTION:
{job_description}

COMPANY CONTEXT FROM KNOWLEDGE BASE (cultural notes, tools, values, team history):
{context_text}

Produce a complete, structured hiring package in clean Markdown. No preamble.

---

## 🧾 Role Summary
(One paragraph: what this person will own, what success looks like in 90 days)

## 📊 Candidate Scorecard Matrix
(Table with columns: Criteria | Weight (%) | Signal/Evidence | Red Flags)
Include 6–8 criteria spanning: technical skill, communication, autonomy, culture-fit,
ownership mindset, tool familiarity (reference context if relevant).

## 🔬 Technical Interview Rubric
(3–5 technical questions or challenges appropriate for the role.
For each: Question | What Good Looks Like | What Poor Looks Like)

## 🤝 Culture-Fit Signal Questions
(3–5 behavioral questions derived from the company context above.
For each: Question | Why We Ask This)

## 🚩 Automatic Disqualifiers
(List of 3–5 hard no's based on the job goals and company culture context)
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content.strip()


# ---------------------------------------------------------------------------
# Combined entry point (used by app.py)
# ---------------------------------------------------------------------------

def run_hiring_assist(
    role_title: str,
    job_description: str,
    model: str = "qwen3:latest",
) -> Dict:
    """
    Single call from app.py.

    Args:
        role_title:       Short role title string
        job_description:  Full role description and goals
        model:            Ollama model

    Returns:
        dict with keys:
            role_title:       str
            context_chunks:   list[dict] — retrieved context
            hiring_package:   str — full markdown hiring package
    """
    if not role_title.strip() or not job_description.strip():
        raise ValueError("[hiring_assist.run] Role title and job description are required.")

    context_chunks = retrieve_hiring_context(job_description, top_k=5)
    hiring_package = generate_hiring_package(
        role_title=role_title,
        job_description=job_description,
        context_chunks=context_chunks,
        model=model,
    )

    return {
        "role_title": role_title,
        "context_chunks": context_chunks,
        "hiring_package": hiring_package,
    }
