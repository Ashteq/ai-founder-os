"""
database.py — AI Founder OS
Handles PostgreSQL + pgvector connection, schema init, and vector CRUD helpers.
Supports local WSL2/Postgres or cloud Neon.tech / Supabase via DATABASE_URL secret.
"""

import os
import psycopg2
import psycopg2.extras
import streamlit as st
from typing import Optional, List, Tuple


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _get_dsn() -> str:
    """
    Return the PostgreSQL DSN string.
    Priority order:
      1. st.secrets["DATABASE_URL"]  (set via .streamlit/secrets.toml or Streamlit Cloud)
      2. DATABASE_URL environment variable
      3. Hard-coded local-dev fallback (localhost, db=founder_os, user=postgres)
    """
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except (KeyError, AttributeError, FileNotFoundError):
        pass

    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url

    # Standard local fallback aligned with trusted local container on port 5433
    return "postgresql://postgres:postgres@localhost:5433/founder_os"


def get_connection() -> psycopg2.extensions.connection:
    """
    Open and return a fresh psycopg2 connection.
    Callers are responsible for closing it (or use a context manager).
    """
    dsn = _get_dsn()
    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    return conn


def ping_database() -> Tuple[bool, str]:
    """
    Quick liveness check used by the sidebar heartbeat widget.
    Returns (success: bool, message: str).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        return True, "● DB ONLINE"
    except Exception as exc:
        return False, f"✕ DB OFFLINE — {exc}"


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

INIT_SQL = """
-- Enable pgvector extension (safe to run repeatedly)
CREATE EXTENSION IF NOT EXISTS vector;

-- Master knowledge table
CREATE TABLE IF NOT EXISTS founder_knowledge (
    id              SERIAL PRIMARY KEY,
    module_source   TEXT        NOT NULL,
    document_title  TEXT        NOT NULL,
    text_chunk      TEXT        NOT NULL,
    embedding       VECTOR(768),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cosine-distance index for fast ANN search (IVFFlat)
-- Created only if it doesn't exist yet.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'founder_knowledge'
          and indexname = 'founder_knowledge_embedding_idx'
    ) THEN
        CREATE INDEX founder_knowledge_embedding_idx
            ON founder_knowledge
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 50);
    END IF;
END
$$;
"""


def init_db() -> None:
    """
    Run schema bootstrap SQL.  Called once from app.py on startup.
    Idempotent — safe to call multiple times.
    """
    dsn = _get_dsn()
    # Masking password for safe terminal log printing
    masked_dsn = dsn
    if "@" in dsn:
        credentials, host_info = dsn.split("@", 1)
        if ":" in credentials:
            prefix, _ = credentials.rsplit(":", 1)
            masked_dsn = f"{prefix}:****@{host_info}"
            
    print(f"\n[DIAGNOSTIC] Schema boot initiating...")
    print(f"[DIAGNOSTIC] Targeted DSN Connection String: {masked_dsn}\n")
    
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(INIT_SQL)
        conn.commit()
        print("[DIAGNOSTIC] Schema bootstrap completed successfully without errors.\n")
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        raise RuntimeError(f"[database.init_db] Schema bootstrap failed: {exc}") from exc
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Vector write helper
# ---------------------------------------------------------------------------

def save_vector_chunk(
    module: str,
    title: str,
    chunk: str,
    embedding_vector: List[float],
) -> int:
    if len(embedding_vector) != 768:
        raise ValueError(
            f"[save_vector_chunk] Expected 768-dim vector, got {len(embedding_vector)}"
        )

    sql = """
        INSERT INTO founder_knowledge
            (module_source, document_title, text_chunk, embedding)
        VALUES (%s, %s, %s, %s::vector)
        RETURNING id;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            vec_literal = "[" + ",".join(str(v) for v in embedding_vector) + "]"
            cur.execute(sql, (module, title, chunk, vec_literal))
            row_id = cur.fetchone()[0]
        conn.commit()
        return row_id
    except Exception as exc:
        conn.rollback()
        raise RuntimeError(f"[save_vector_chunk] Insert failed: {exc}") from exc
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Vector query helper
# ---------------------------------------------------------------------------

def query_vector_similarity(
    query_vector: List[float],
    limit: int = 3,
    module_filter: Optional[str] = None,
) -> List[dict]:
    if len(query_vector) != 768:
        raise ValueError(
            f"[query_vector_similarity] Expected 768-dim vector, got {len(query_vector)}"
        )

    vec_literal = "[" + ",".join(str(v) for v in query_vector) + "]"

    if module_filter:
        sql = """
            SELECT
                id,
                module_source,
                document_title,
                text_chunk,
                created_at,
                embedding <=> %s::vector AS distance
            FROM founder_knowledge
            WHERE module_source = %s
            ORDER BY distance ASC
            LIMIT %s;
        """
        params = (vec_literal, module_filter, limit)
    else:
        sql = """
            SELECT
                id,
                module_source,
                document_title,
                text_chunk,
                created_at,
                embedding <=> %s::vector AS distance
            FROM founder_knowledge
            ORDER BY distance ASC
            LIMIT %s;
        """
        params = (vec_literal, limit)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as exc:
        raise RuntimeError(
            f"[query_vector_similarity] Query failed: {exc}"
        ) from exc
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Stats helper (sidebar telemetry)
# ---------------------------------------------------------------------------

def get_db_stats() -> dict:
    sql_total = "SELECT COUNT(*) FROM founder_knowledge;"
    sql_by_module = """
        SELECT module_source, COUNT(*) AS cnt
        FROM founder_knowledge
        GROUP BY module_source
        ORDER BY cnt DESC;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_total)
            total = cur.fetchone()[0]
            cur.execute(sql_by_module)
            rows = cur.fetchall()
        by_module = [{"module": r[0], "count": r[1]} for r in rows]
        return {"total": total, "by_module": by_module}
    except Exception as exc:
        return {"total": "N/A", "by_module": [], "error": str(exc)}
    finally:
        conn.close()