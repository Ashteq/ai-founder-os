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
# Embedding helper (VERSION-PROOF)
# ---------------------------------------------------------------------------

def embed_text(text: str) -> List[float]:
    """
    Call local Ollama nomic-embed-text model to get a 768-dim embedding.
    Safely handles both v0.1.x (embeddings) and v0.2.x+ (embed) API changes.
    """
    try:
        # 1. Try modern version API
        if hasattr(ollama, 'embed'):
            response = ollama.embed(model="nomic-embed-text", input=text)
            
            # Extract safely if it's a dict or object
            if isinstance(response, dict):
                embs = response.get("embeddings", [])
                return embs[0] if (embs and isinstance(embs[0], list)) else embs
            else:
                return response.embeddings[0]
                
        # 2. Try legacy version API fallback
        else:
            response = ollama.embeddings(model="nomic-embed-text", prompt=text)
            
            if isinstance(response, dict):
                return response.get("embedding", [])
            else:
                return response.embedding
                
    except Exception as e:
        raise RuntimeError(f"[meeting_intel.embed_text] Vector generation failed: {str(e)}")


# ---------------------------------------------------------------------------
# Ingest pipeline
# ---------------------------------------------------------------------------

def ingest_meeting_notes(title: str, raw_text: str) -> Dict:
    """
    Full pipeline to chunk, embed, and save to DB.
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
# Analysis pipeline (VERSION-PROOF)
# ---------------------------------------------------------------------------

def analyze_meeting(title: str, raw_text: str, model: str = "gemma:2b") -> str:
    """
    Use Ollama to generate a structured markdown analysis of the meeting.
    """
    # Truncate raw text to ~6000 chars to stay within context safely
    truncated = raw_text[:6000] if len(raw_text) > 6000 else raw_text

    prompt = f"""You are a Chief-of-Staff assistant for a startup founder.
Analyze the following meeting notes and produce a concise, structured report.

Meeting Title: {title}

--- MEETING NOTES START ---
{truncated}
--- MEETING NOTES END ---

Respond ONLY in clean Markdown with exactly three sections, no preamble. Ensure proper line breaks.

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
    
    # ---------------------------------------------------------
    # Safely parse the response regardless of Ollama version
    # and sanitize the Markdown for Streamlit rendering.
    # ---------------------------------------------------------
    try:
        if isinstance(response, dict):
            raw_text = response.get('message', {}).get('content', '').strip()
        else:
            raw_text = response.message.content.strip()
            
        # Streamlit Markdown Sanitizer
        lines = raw_text.splitlines()
        processed_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("-", "*", "#", "|", "1.", "[", "─")):
                processed_lines.append(line)
            elif stripped == "":
                processed_lines.append("")
            else:
                processed_lines.append(line + "  ")
                
        return "\n".join(processed_lines)
            
    except Exception as e:
        raise RuntimeError(f"[analyze_meeting] Failed to parse LLM response: {str(e)}")


# ---------------------------------------------------------------------------
# Combined entry point (used by app.py)
# ---------------------------------------------------------------------------

def run_meeting_intel(title: str, raw_text: str, model: str = "gemma:2b") -> Dict:
    """
    Single call from app.py
    """
    ingest_result = ingest_meeting_notes(title=title, raw_text=raw_text)
    analysis = analyze_meeting(title=title, raw_text=raw_text, model=model)
    return {
        "ingest_result": ingest_result,
        "analysis": analysis,
    }