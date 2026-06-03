"""
task_manager.py — AI Founder OS  |  Module 2: Task Manager
Accepts raw task strings, vectorizes them, retrieves top-3 semantically
relevant knowledge-base chunks (past meeting notes, blockers, context),
then generates an intelligent re-prioritized daily execution roadmap via Ollama.
"""

from typing import List, Dict
import ollama
import database
import meeting_intel  # reuse embed_text


# ---------------------------------------------------------------------------
# Retrieve context for a batch of tasks
# ---------------------------------------------------------------------------

def retrieve_task_context(tasks: List[str], top_k: int = 3) -> List[Dict]:
    """
    For the full list of tasks (joined as one query), fetch the top-k most
    semantically relevant chunks from the vector store.
    """
    if not tasks:
        return []

    # Join all tasks into one representative query embedding
    combined_query = " | ".join(tasks)
    query_embedding = meeting_intel.embed_text(combined_query)
    context_chunks = database.query_vector_similarity(
        query_vector=query_embedding,
        limit=top_k,
    )
    return context_chunks


# ---------------------------------------------------------------------------
# Roadmap generation (VERSION-PROOF)
# ---------------------------------------------------------------------------

def generate_task_roadmap(
    tasks: List[str],
    context_chunks: List[Dict],
    model: str = "qwen3:latest",
) -> str:
    """
    Send tasks + retrieved context to Ollama and get back an intelligent,
    re-prioritized daily execution roadmap with estimated time blocks.
    """
    # Format the retrieved context blocks for the prompt
    context_text = ""
    if context_chunks:
        context_sections = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("module_source", "unknown")
            title = chunk.get("document_title", "untitled")
            text = chunk.get("text_chunk", "")
            dist = chunk.get("distance", 0)
            context_sections.append(
                f"[Context {i} | source: {source} | doc: {title} | similarity: {1 - float(dist):.2f}]\n{text}"
            )
        context_text = "\n\n".join(context_sections)
    else:
        context_text = "No prior context available in the knowledge base."

    # Format raw tasks
    tasks_formatted = "\n".join(f"- {t.strip()}" for t in tasks if t.strip())

    prompt = f"""You are an expert Chief-of-Staff and execution coach for a startup founder.
Your job is to produce an intelligent, re-prioritized daily roadmap.

CONTEXT FROM KNOWLEDGE BASE (past meetings, blockers, decisions):
{context_text}

RAW TASKS FROM FOUNDER TODAY:
{tasks_formatted}

Using the context above to understand constraints, blockers, and background, produce a structured daily execution plan.

Respond ONLY in clean Markdown with this structure, no preamble:

## 🗺️ Daily Execution Roadmap

### Priority Tier 1 — Critical (Do First)
(Tasks that are blocked by others, time-sensitive, or high-impact. Include estimated time block.)

### Priority Tier 2 — Core Progress (Do Second)
(Important but not urgent tasks that move key projects forward.)

### Priority Tier 3 — Maintenance & Admin (Do Last or Delegate)
(Low-cognitive-load tasks, communications, reviews.)

## ⏱️ Estimated Day Timeline
(Lay out a simple hour-by-hour schedule block, e.g.: 09:00–10:30 | Task X)

## 🔍 Context-Informed Flags
(Note any task that has a known blocker or constraint from the retrieved knowledge base context. If none, write "None flagged.")
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    
    # ---------------------------------------------------------
    # Safely parse the response regardless of Ollama version
    # ---------------------------------------------------------
    try:
        if isinstance(response, dict):
            return response.get('message', {}).get('content', '').strip()
        else:
            return response.message.content.strip()
    except Exception as e:
        raise RuntimeError(f"[generate_task_roadmap] Failed to parse LLM response: {str(e)}")


# ---------------------------------------------------------------------------
# Combined entry point (used by app.py)
# ---------------------------------------------------------------------------

def run_task_manager(
    raw_tasks_text: str,
    model: str = "qwen3:latest",
) -> Dict:
    """
    Single call from app.py.
    """
    # Parse line-separated tasks, strip blanks
    tasks = [line.strip() for line in raw_tasks_text.splitlines() if line.strip()]
    if not tasks:
        raise ValueError("[task_manager.run] No tasks provided.")

    context_chunks = retrieve_task_context(tasks, top_k=3)
    roadmap = generate_task_roadmap(
        tasks=tasks,
        context_chunks=context_chunks,
        model=model,
    )

    return {
        "tasks": tasks,
        "context_chunks": context_chunks,
        "roadmap": roadmap,
    }