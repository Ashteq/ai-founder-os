"""
meeting_intel.py — AI Founder OS  |  Module 1: Meeting Intelligence
Ingests raw meeting transcripts or notes, chunks them, vectorizes via
nomic-embed-text (Ollama), stores to pgvector, and returns a structured
markdown analysis: summary, action items, and risk flags.
"""

from typing import List, Dict
import ollama
import database


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:
    """
    Split `text` into overlapping character-window chunks.

    Args:
        text:       Raw input string (transcript / notes)
        chunk_size: Maximum characters per chunk
        overlap:    Character overlap between consecutive chunks to preserve
                    sentence continuity

    Returns:
        List of non-empty string chunks.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at a sentence boundary (. ! ?) within the last 80 chars
        if end < text_len:
            search_region = text[max(start, end - 80): end]
            for punct in (".", "!", "?"):
                pos = search_region.rfind(punct)
                if pos != -1:
                    end = max(start, end - 80) + pos + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Next window starts `overlap` chars before the current end
        start = end - overlap if end < text_len else text_len

    return chunks


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

def embed_text(text: str) -> List[float]:
    """
    Call local Ollama nomic-embed-text model to get a 768-dim embedding.

    Args:
        text: String to embed (will be truncated to ~8192 tokens by model)

    Returns:
        List[float] of length 768
    """
    response = ollama.embed(model="nomic-embed-text", input=text)
    # ollama.embed returns an EmbedResponse with an `embeddings` attribute
    # which is a list of embedding vectors (one per input string).
    embedding = response.embeddings[0]
    return embedding


# ---------------------------------------------------------------------------
# Ingest pipeline
# ---------------------------------------------------------------------------

def ingest_meeting_notes(title: str, raw_text: str) -> Dict:
    """
    Full pipeline:
      1. Chunk raw_text
      2. Embed each chunk via nomic-embed-text
      3. Persist chunks + embeddings to founder_knowledge (module='meeting_intel')
      4. Return dict with chunk count and list of saved chunk IDs

    Args:
        title:    Document label (meeting name / date)
        raw_text: Full raw transcript or notes text

    Returns:
        dict with keys: chunks_saved (int), saved_ids (list[int])
    """
    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("[meeting_intel.ingest] No text content to process.")

    saved_ids: List[int] = []
    for chunk in chunks:
        embedding = embed_text(chunk)
        row_id = database.save_vector_chunk(
            module="meeting_intel",
            title=title,
            chunk=chunk,
            embedding_vector=embedding,
        )
        saved_ids.append(row_id)

    return {"chunks_saved": len(saved_ids), "saved_ids": saved_ids}


# ---------------------------------------------------------------------------
# Analysis pipeline
# ---------------------------------------------------------------------------

def analyze_meeting(title: str, raw_text: str, model: str = "qwen3:latest") -> str:
    """
    Use Ollama to generate a structured markdown analysis of the meeting.

    Returns a markdown string containing:
      ## Summary
      ## Action Items
      ## Risks & Blockers

    Args:
        title:    Meeting label (used in the prompt for context)
        raw_text: Full raw text of the meeting notes / transcript
        model:    Ollama model to use for generation
    """
    # Truncate raw text to ~6000 chars to stay within context safely
    truncated = raw_text[:6000] if len(raw_text) > 6000 else raw_text

    prompt = f"""You are a Chief-of-Staff assistant for a startup founder.
Analyze the following meeting notes and produce a concise, structured report.

Meeting Title: {title}

--- MEETING NOTES START ---
{truncated}
--- MEETING NOTES END ---

Respond ONLY in clean Markdown with exactly three sections, no preamble:

## 📋 Summary
(2–4 sentence executive summary of what was discussed and decided)

## ✅ Action Items
(Bullet list of concrete next steps, each prefixed with an owner name if mentioned, or "Founder" as default. Format: `- [ ] [Owner]: Action`)

## ⚠️ Risks & Blockers
(Bullet list of any risks, blockers, open questions, or unresolved dependencies identified. If none, write "None identified.")
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content.strip()


# ---------------------------------------------------------------------------
# Combined entry point (used by app.py)
# ---------------------------------------------------------------------------

def run_meeting_intel(title: str, raw_text: str, model: str = "qwen3:latest") -> Dict:
    """
    Single call from app.py that:
      1. Ingests and vectorizes the notes into the DB
      2. Generates and returns the markdown analysis

    Returns:
        dict with keys:
            ingest_result: dict (chunks_saved, saved_ids)
            analysis:      str (markdown)
    """
    ingest_result = ingest_meeting_notes(title=title, raw_text=raw_text)
    analysis = analyze_meeting(title=title, raw_text=raw_text, model=model)
    return {
        "ingest_result": ingest_result,
        "analysis": analysis,
    }
