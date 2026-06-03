"""
planner.py — AI Founder OS  |  Module 4: Strategic Planner
Evaluates weekly strategic goals against the aggregate of latest notes and
blockers pulled directly from the vector index. Produces a strategic risk
audit with conflict flags, timeline assessments, and execution recommendations.
"""

from typing import List, Dict, Tuple
import ollama
import database
import meeting_intel  # reuse embed_text


# ---------------------------------------------------------------------------
# Context aggregation
# ---------------------------------------------------------------------------

def retrieve_strategic_context(
    weekly_goals: str,
    top_k: int = 6,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Pull two sets of context from the vector store:
      1. Semantically relevant chunks to the goals (across all modules)
      2. Recent blocker/risk mentions specifically from meeting_intel

    Args:
        weekly_goals: Raw weekly goals text
        top_k:        Number of chunks to retrieve per query

    Returns:
        Tuple of (goal_context: list[dict], blocker_context: list[dict])
    """
    goals_embedding = meeting_intel.embed_text(weekly_goals)

    # General semantic match across all modules
    goal_context = database.query_vector_similarity(
        query_vector=goals_embedding,
        limit=top_k,
    )

    # Focused pull from meeting notes for blockers/risks
    blocker_query = weekly_goals + " blockers constraints risks timeline delays dependencies"
    blocker_embedding = meeting_intel.embed_text(blocker_query)
    blocker_context = database.query_vector_similarity(
        query_vector=blocker_embedding,
        limit=top_k,
        module_filter="meeting_intel",
    )

    return goal_context, blocker_context


# ---------------------------------------------------------------------------
# Strategic risk audit
# ---------------------------------------------------------------------------

def generate_strategic_plan(
    weekly_goals: str,
    goal_context: List[Dict],
    blocker_context: List[Dict],
    model: str = "qwen3:latest",
) -> str:
    """
    Generate a strategic risk audit and execution plan using Ollama.

    Args:
        weekly_goals:    Raw text of the founder's weekly strategic goals
        goal_context:    Semantically relevant knowledge-base chunks
        blocker_context: Meeting-intel focused blocker chunks
        model:           Ollama model

    Returns:
        Markdown string: risk audit report
    """
    def _format_chunks(chunks: List[Dict], label: str) -> str:
        if not chunks:
            return f"No {label} context available."
        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("module_source", "unknown")
            title = chunk.get("document_title", "untitled")
            text = chunk.get("text_chunk", "")
            dist = chunk.get("distance", 0)
            parts.append(
                f"[{label} {i} | src: {source} | doc: {title} | match: {1 - float(dist):.2f}]\n{text}"
            )
        return "\n\n".join(parts)

    goal_ctx_text = _format_chunks(goal_context, "GoalContext")
    blocker_ctx_text = _format_chunks(blocker_context, "BlockerContext")

    prompt = f"""You are a strategic advisor and Chief-of-Staff for a startup founder.
Your task is to produce an honest, data-driven strategic risk audit for the upcoming week.

THIS WEEK'S GOALS:
{weekly_goals}

RELEVANT KNOWLEDGE BASE CONTEXT (past decisions, updates, constraints):
{goal_ctx_text}

BLOCKER & RISK SIGNALS FROM MEETING NOTES:
{blocker_ctx_text}

Produce a full strategic planning report in clean Markdown. No preamble.

---

## 🎯 Goal Alignment Assessment
(Evaluate each stated goal: Is it realistic this week? Is it aligned with prior decisions?
Rate each goal: ✅ On Track | ⚠️ At Risk | ❌ Blocked)

| Goal | Status | Reasoning |
|------|--------|-----------|
(Fill in one row per goal)

## 🔥 Risk Audit Score
(Give an overall execution risk score out of 10, with 10 = very high risk.
Justify with 2–3 sentences.)

**Risk Score: X / 10**

## ⛔ Timeline Conflicts Detected
(List any goals that conflict with each other, depend on unresolved blockers,
or have unrealistic timelines given the context. Be specific.)

## 📐 Strategic Recommendations
(3–5 concrete, actionable recommendations to maximize the week's output
and de-risk the identified conflicts.)

## 📅 Suggested Weekly Focus Order
(Simple ordered list of what to tackle Monday–Friday, with a one-line rationale per day.)
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content.strip()


# ---------------------------------------------------------------------------
# Combined entry point (used by app.py)
# ---------------------------------------------------------------------------

def run_planner(
    weekly_goals_text: str,
    model: str = "qwen3:latest",
) -> Dict:
    """
    Single call from app.py.

    Args:
        weekly_goals_text: Raw newline-or-paragraph weekly goals
        model:             Ollama model

    Returns:
        dict with keys:
            goal_context:    list[dict] — general context chunks
            blocker_context: list[dict] — blocker-focused chunks
            strategic_plan:  str — full markdown strategic audit
    """
    if not weekly_goals_text.strip():
        raise ValueError("[planner.run] Weekly goals text is required.")

    goal_context, blocker_context = retrieve_strategic_context(
        weekly_goals=weekly_goals_text,
        top_k=6,
    )
    strategic_plan = generate_strategic_plan(
        weekly_goals=weekly_goals_text,
        goal_context=goal_context,
        blocker_context=blocker_context,
        model=model,
    )

    return {
        "goal_context": goal_context,
        "blocker_context": blocker_context,
        "strategic_plan": strategic_plan,
    }
