"""
app.py — AI Founder OS
Core Streamlit interface: retro MS95 × ChipTiles aesthetic,
sidebar DB/model telemetry, four module tabs, A.Sh watermark footer.
"""

import streamlit as st
import database
import meeting_intel
import task_manager
import hiring_assist
import planner

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG — must be the first Streamlit call
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Founder OS",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# DB BOOTSTRAP
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def bootstrap_database():
    """Run schema init once per app session (cached so it doesn't repeat)."""
    try:
        database.init_db()
        return True, "OK"
    except Exception as exc:
        return False, str(exc)

_db_boot_ok, _db_boot_msg = bootstrap_database()

# ═══════════════════════════════════════════════════════════════════════════
# RETRO GLOBAL CSS INJECTION
# ═══════════════════════════════════════════════════════════════════════════
RETRO_CSS = """
<style>
/* ── Global cursor ── */
*, *::before, *::after {
    cursor: url('https://cur.cursors-4u.net/games/gam-4/gam384.cur'), default !important;
}
a, button, [role="button"], .stButton > button, .stTabs [role="tab"] {
    cursor: url('https://cur.cursors-4u.net/games/gam-4/gam384.cur'), pointer !important;
}

/* ── Google font fallback — pixel/mono feel ── */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #D6D2C4;
    --card:      #F0EDE6;
    --border:    #2B2625;
    --accent1:   #FF6B35;
    --accent2:   #F7C143;
    --text:      #111111;
    --muted:     #5a5450;
    --font:      'Share Tech Mono', 'Courier New', Courier, monospace;
    --shadow:    inset 2px 2px 0 #ffffff, inset -2px -2px 0 #888880;
}

/* ── App background ── */
.stApp, .main > div {
    background-color: var(--bg) !important;
    font-family: var(--font) !important;
}

/* ── Global text ── */
body, p, span, label, div, li, td, th,
.stMarkdown, .stText, .element-container {
    font-family: var(--font) !important;
    color: var(--text) !important;
}

h1, h2, h3 {
    font-family: var(--font) !important;
    color: var(--text) !important;
    letter-spacing: 0.04em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--card) !important;
    border-right: 3px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font) !important;
}

/* ── Containers / cards ── */
[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stForm"],
.stContainer {
    background-color: var(--card) !important;
    border: 2px solid var(--border) !important;
    box-shadow: var(--shadow) !important;
    border-radius: 0 !important;
    padding: 12px !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: var(--accent1) !important;
    color: #fff !important;
    border: 2px solid var(--border) !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow) !important;
    font-family: var(--font) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 6px 16px !important;
    transition: none !important;
}
.stButton > button:hover {
    background-color: var(--accent2) !important;
    color: var(--text) !important;
}
.stButton > button:active {
    box-shadow: inset 2px 2px 0 #888880, inset -2px -2px 0 #ffffff !important;
    transform: translateY(1px) !important;
}

/* ── Text inputs / textareas ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background-color: #ffffff !important;
    border: 2px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    color: var(--text) !important;
    box-shadow: inset 2px 2px 0 #aaa8a0 !important;
}

/* ── Tabs ── */
.stTabs [role="tablist"] {
    background-color: var(--bg) !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 2px !important;
}
.stTabs [role="tab"] {
    background-color: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-bottom: none !important;
    border-radius: 0 !important;
    font-family: var(--font) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    padding: 4px 14px !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    background-color: var(--accent2) !important;
    color: var(--text) !important;
    font-weight: bold !important;
}

/* ── Markdown code / pre blocks ── */
code, pre {
    font-family: var(--font) !important;
    background-color: #e8e5de !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    padding: 2px 4px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    color: var(--accent1) !important;
}

/* ── Progress / metric ── */
[data-testid="metric-container"] {
    background-color: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 0 !important;
    padding: 8px !important;
}

/* ── Scrollbar retro ── */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: var(--bg); border: 1px solid var(--border); }
::-webkit-scrollbar-thumb {
    background: #9a9890;
    border: 2px solid var(--border);
    border-radius: 0;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent1); }

/* ── Select / dropdown ── */
select, option {
    font-family: var(--font) !important;
    background-color: #ffffff !important;
    border: 2px solid var(--border) !important;
    border-radius: 0 !important;
}
</style>
"""

st.markdown(RETRO_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# WATERMARK FOOTER (fixed bottom bar)
# ═══════════════════════════════════════════════════════════════════════════
WATERMARK_HTML = """
<style>
.ash-watermark {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background-color: #E6E4DD;
    border-top: 2px solid #2B2625;
    padding: 4px 16px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
}
.ash-watermark-text {
    font-family: 'Share Tech Mono', 'Courier New', Courier, monospace;
    font-size: 0.68rem;
    color: #5a5450;
    letter-spacing: 0.08em;
    border: 1px solid #2B2625;
    padding: 2px 10px;
    background-color: #F0EDE6;
    user-select: none;
}
</style>
<div class="ash-watermark">
    <span class="ash-watermark-text">System Core Engine running under license: A.Sh</span>
</div>
"""
st.markdown(WATERMARK_HTML, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div style="
        border: 3px solid #2B2625;
        background: linear-gradient(90deg, #FF6B35 0%, #F7C143 100%);
        padding: 10px 20px;
        margin-bottom: 16px;
        box-shadow: inset 2px 2px 0 #ffffff, inset -2px -2px 0 #888880;
    ">
        <span style="
            font-family: 'Share Tech Mono', 'Courier New', monospace;
            font-size: 1.6rem;
            color: #111111;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        ">🖥️ AI FOUNDER OS &nbsp; <span style="font-size:0.9rem; opacity:0.7">v1.0 — Chief-of-Staff Intelligence Suite</span></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div style="
            border: 2px solid #2B2625;
            background-color: #F7C143;
            padding: 6px 12px;
            margin-bottom: 12px;
            text-align: center;
        ">
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.9rem;
                         text-transform:uppercase; letter-spacing:0.08em; color:#111;">
                ░░ SYSTEM PANEL ░░
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── DB Heartbeat ──
    st.markdown("**[ DB HEARTBEAT ]**")
    db_ok, db_msg = database.ping_database()
    status_color = "#3cb371" if db_ok else "#cc3333"
    st.markdown(
        f'<div style="border:2px solid #2B2625; padding:6px 10px; background:#F0EDE6; '
        f'font-family:\'Share Tech Mono\',monospace; font-size:0.8rem; '
        f'color:{status_color}; margin-bottom:8px;">{db_msg}</div>',
        unsafe_allow_html=True,
    )

    if not _db_boot_ok:
        st.markdown(
            f'<div style="border:2px solid #cc3333; padding:6px 10px; background:#ffe0e0; '
            f'font-family:\'Share Tech Mono\',monospace; font-size:0.72rem; color:#cc3333; '
            f'margin-bottom:8px;">⚠ Schema boot failed:<br>{_db_boot_msg}</div>',
            unsafe_allow_html=True,
        )

    # ── Model Selector ──
    st.markdown("**[ ACTIVE LLM ]**")
    selected_model = st.selectbox(
        label="Ollama Model",
        options=[
            "qwen3:latest",
            "gemma3:latest",
            "llama3.1:latest",
            "mistral:latest",
            "phi3:latest",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div style="border:2px solid #2B2625; padding:6px 10px; background:#F0EDE6; '
        f'font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; '
        f'color:#111; margin-bottom:8px;">⚙ MODEL: {selected_model}</div>',
        unsafe_allow_html=True,
    )

    # ── DB Stats Telemetry ──
    st.markdown("**[ KNOWLEDGE BASE ]**")
    if st.button("⟳ REFRESH STATS", key="refresh_stats"):
        st.cache_resource.clear()

    if db_ok:
        stats = database.get_db_stats()
        total = stats.get("total", 0)
        by_module = stats.get("by_module", [])
        st.markdown(
            f'<div style="border:2px solid #2B2625; padding:8px 12px; background:#F0EDE6; '
            f'font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; margin-bottom:4px;">'
            f'TOTAL CHUNKS: <b>{total}</b></div>',
            unsafe_allow_html=True,
        )
        for mod_stat in by_module:
            mod = mod_stat.get("module", "?")
            cnt = mod_stat.get("count", 0)
            bar_pct = min(int((cnt / max(total, 1)) * 100), 100) if total else 0
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.72rem; '
                f'color:#5a5450; margin:2px 0;">'
                f'{mod[:18]}: {cnt} '
                f'<span style="color:#FF6B35">{"█" * (bar_pct // 10)}{"░" * (10 - bar_pct // 10)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.75rem; '
            'color:#cc3333; padding:4px 0;">Stats unavailable — DB offline</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── System info ──
    st.markdown(
        '<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; '
        'color:#8a8680; line-height:1.7;">'
        'AI Founder OS<br>'
        'Build: 1.0.0-stable<br>'
        'Embed model: nomic-embed-text<br>'
        'Vector dim: 768<br>'
        'Store: PostgreSQL + pgvector'
        '</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════════════════
TAB_LABELS = [
    "📝 MEETING INTEL",
    "✅ TASK MANAGER",
    "🧑‍💼 HIRING ASSIST",
    "📅 STRATEGIC PLANNER",
]

tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

# ─────────────────────────────────────────────────────────────────────────
# TAB 1 — MEETING INTEL
# ─────────────────────────────────────────────────────────────────────────
with tab1:
    with st.container(border=True):
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace; font-size:1.05rem; '
            'text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid #2B2625; '
            'padding-bottom:6px; margin-bottom:14px;">MODULE 1 — Meeting Intelligence Engine</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; '
            'color:#5a5450;">Paste raw meeting notes or transcript. System will chunk, vectorize, '
            'store to knowledge base, and generate analysis.</span>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        col1, col2 = st.columns([1, 2])
        with col1:
            meeting_title = st.text_input(
                "Meeting / Document Title",
                placeholder="e.g. Investor Sync — 2025-07-14",
                key="meeting_title",
            )
        with col2:
            st.markdown("")  # spacer

        meeting_notes = st.text_area(
            "Raw Meeting Notes / Transcript",
            height=260,
            placeholder="Paste the full meeting transcript, notes, or discussion summary here...\n\nExample:\nJohn: We need to ship the auth module by end of Q3.\nSarah: The backend dependency isn't resolved yet — blocked on AWS IAM config.\n...",
            key="meeting_notes",
        )

        run_meeting = st.button("▶ PROCESS MEETING INTEL", key="run_meeting")

    if run_meeting:
        if not meeting_title.strip():
            st.error("Please enter a meeting title.")
        elif not meeting_notes.strip():
            st.error("Please paste meeting notes before processing.")
        else:
            with st.spinner("Chunking → Embedding → Storing → Analyzing..."):
                try:
                    result = meeting_intel.run_meeting_intel(
                        title=meeting_title.strip(),
                        raw_text=meeting_notes.strip(),
                        model=selected_model,
                    )
                    ingest = result["ingest_result"]
                    analysis = result["analysis"]

                    with st.container(border=True):
                        st.markdown(
                            '<div style="font-family:\'Share Tech Mono\',monospace; '
                            'font-size:0.85rem; color:#3cb371; margin-bottom:8px;">'
                            f'✓ INGESTED {ingest["chunks_saved"]} CHUNKS — IDs: '
                            f'{ingest["saved_ids"][:5]}{"..." if len(ingest["saved_ids"]) > 5 else ""}'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown("---")
                        st.markdown(analysis)

                except Exception as exc:
                    st.error(f"Processing error: {exc}")

# ─────────────────────────────────────────────────────────────────────────
# TAB 2 — TASK MANAGER
# ─────────────────────────────────────────────────────────────────────────
with tab2:
    with st.container(border=True):
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace; font-size:1.05rem; '
            'text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid #2B2625; '
            'padding-bottom:6px; margin-bottom:14px;">MODULE 2 — RAG-Augmented Task Prioritizer</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; '
            'color:#5a5450;">Enter tasks one per line. System retrieves relevant context from '
            'knowledge base and generates a prioritized execution roadmap.</span>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        raw_tasks = st.text_area(
            "Today's Raw Tasks (one per line)",
            height=220,
            placeholder="Review investor deck slides\nFinalize API contract with partner\nUnblock backend team on auth issue\nPost week summary to team Slack\nSchedule design review for mobile app\nReview Q3 hiring pipeline",
            key="raw_tasks",
        )

        run_tasks = st.button("▶ GENERATE EXECUTION ROADMAP", key="run_tasks")

    if run_tasks:
        if not raw_tasks.strip():
            st.error("Please enter at least one task.")
        else:
            with st.spinner("Embedding tasks → Querying vector DB → Generating roadmap..."):
                try:
                    result = task_manager.run_task_manager(
                        raw_tasks_text=raw_tasks.strip(),
                        model=selected_model,
                    )
                    tasks_parsed = result["tasks"]
                    context_chunks = result["context_chunks"]
                    roadmap = result["roadmap"]

                    with st.container(border=True):
                        # Show parsed tasks
                        st.markdown(
                            f'<div style="font-family:\'Share Tech Mono\',monospace; '
                            f'font-size:0.8rem; color:#5a5450; margin-bottom:6px;">'
                            f'PARSED {len(tasks_parsed)} TASKS | RETRIEVED {len(context_chunks)} CONTEXT CHUNKS'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        # Show context chunks in expander
                        if context_chunks:
                            with st.expander("► Retrieved Knowledge Base Context", expanded=False):
                                for i, chunk in enumerate(context_chunks, 1):
                                    src = chunk.get("module_source", "?")
                                    title = chunk.get("document_title", "?")
                                    text = chunk.get("text_chunk", "")[:300]
                                    dist = float(chunk.get("distance", 0))
                                    st.markdown(
                                        f'<div style="border-left:3px solid #FF6B35; padding:4px 10px; '
                                        f'margin:6px 0; font-family:\'Share Tech Mono\',monospace; '
                                        f'font-size:0.75rem; background:#F0EDE6;">'
                                        f'<b>[{i}] {src} — {title}</b> (sim: {1-dist:.2f})<br>'
                                        f'<span style="color:#5a5450">{text}{"..." if len(chunk.get("text_chunk","")) > 300 else ""}</span>'
                                        f'</div>',
                                        unsafe_allow_html=True,
                                    )

                        st.markdown("---")
                        st.markdown(roadmap)

                except Exception as exc:
                    st.error(f"Processing error: {exc}")

# ─────────────────────────────────────────────────────────────────────────
# TAB 3 — HIRING ASSIST
# ─────────────────────────────────────────────────────────────────────────
with tab3:
    with st.container(border=True):
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace; font-size:1.05rem; '
            'text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid #2B2625; '
            'padding-bottom:6px; margin-bottom:14px;">MODULE 3 — Hiring Intelligence System</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; '
            'color:#5a5450;">Provide role details. System cross-references cultural context '
            'from knowledge base and generates a complete scorecard + interview rubric.</span>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        role_title = st.text_input(
            "Role Title",
            placeholder="e.g. Senior Full-Stack Engineer",
            key="role_title",
        )
        job_desc = st.text_area(
            "Job Goals & Description",
            height=200,
            placeholder="Describe what you need:\n- Own the backend infrastructure\n- Ship the v2 API within 60 days\n- Work closely with a 3-person product team\n- Must be experienced with AWS, FastAPI, and PostgreSQL\n- Values: high autonomy, async-first, strong written communication",
            key="job_desc",
        )

        run_hiring = st.button("▶ GENERATE HIRING PACKAGE", key="run_hiring")

    if run_hiring:
        if not role_title.strip():
            st.error("Please enter a role title.")
        elif not job_desc.strip():
            st.error("Please enter a job description.")
        else:
            with st.spinner("Retrieving cultural context → Generating scorecard + rubric..."):
                try:
                    result = hiring_assist.run_hiring_assist(
                        role_title=role_title.strip(),
                        job_description=job_desc.strip(),
                        model=selected_model,
                    )
                    context_chunks = result["context_chunks"]
                    hiring_package = result["hiring_package"]

                    with st.container(border=True):
                        st.markdown(
                            f'<div style="font-family:\'Share Tech Mono\',monospace; '
                            f'font-size:0.8rem; color:#5a5450; margin-bottom:6px;">'
                            f'ROLE: {result["role_title"]} | CONTEXT CHUNKS RETRIEVED: {len(context_chunks)}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if context_chunks:
                            with st.expander("► Cultural & Historical Context Used", expanded=False):
                                for i, chunk in enumerate(context_chunks, 1):
                                    src = chunk.get("module_source", "?")
                                    title = chunk.get("document_title", "?")
                                    text = chunk.get("text_chunk", "")[:300]
                                    dist = float(chunk.get("distance", 0))
                                    st.markdown(
                                        f'<div style="border-left:3px solid #F7C143; padding:4px 10px; '
                                        f'margin:6px 0; font-family:\'Share Tech Mono\',monospace; '
                                        f'font-size:0.75rem; background:#F0EDE6;">'
                                        f'<b>[{i}] {src} — {title}</b> (sim: {1-dist:.2f})<br>'
                                        f'<span style="color:#5a5450">{text}{"..." if len(chunk.get("text_chunk","")) > 300 else ""}</span>'
                                        f'</div>',
                                        unsafe_allow_html=True,
                                    )

                        st.markdown("---")
                        st.markdown(hiring_package)

                except Exception as exc:
                    st.error(f"Processing error: {exc}")

# ─────────────────────────────────────────────────────────────────────────
# TAB 4 — STRATEGIC PLANNER
# ─────────────────────────────────────────────────────────────────────────
with tab4:
    with st.container(border=True):
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace; font-size:1.05rem; '
            'text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid #2B2625; '
            'padding-bottom:6px; margin-bottom:14px;">MODULE 4 — Strategic Risk Planner</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; '
            'color:#5a5450;">Input weekly strategic goals. System evaluates them against '
            'knowledge base context, surfaces conflicts, and outputs a risk-scored execution plan.</span>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        weekly_goals = st.text_area(
            "Weekly Strategic Goals",
            height=220,
            placeholder="Enter this week's key goals:\n\n1. Close Series A lead investor by Friday\n2. Ship mobile app v1.2 to TestFlight\n3. Complete Q3 OKR mid-point review with team\n4. Resolve critical auth blocker in backend API\n5. Conduct 3 candidate interviews for CTO role\n6. Finalize partnership terms with Stripe integration partner",
            key="weekly_goals",
        )

        run_planner_btn = st.button("▶ RUN STRATEGIC RISK AUDIT", key="run_planner")

    if run_planner_btn:
        if not weekly_goals.strip():
            st.error("Please enter weekly goals.")
        else:
            with st.spinner("Retrieving strategic context → Running risk audit..."):
                try:
                    result = planner.run_planner(
                        weekly_goals_text=weekly_goals.strip(),
                        model=selected_model,
                    )
                    goal_ctx = result["goal_context"]
                    blocker_ctx = result["blocker_context"]
                    strategic_plan = result["strategic_plan"]

                    with st.container(border=True):
                        st.markdown(
                            f'<div style="font-family:\'Share Tech Mono\',monospace; '
                            f'font-size:0.8rem; color:#5a5450; margin-bottom:6px;">'
                            f'GOAL CONTEXT CHUNKS: {len(goal_ctx)} | BLOCKER CONTEXT CHUNKS: {len(blocker_ctx)}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if goal_ctx:
                                with st.expander("► Goal Context Retrieved", expanded=False):
                                    for i, chunk in enumerate(goal_ctx, 1):
                                        src = chunk.get("module_source", "?")
                                        title = chunk.get("document_title", "?")
                                        text = chunk.get("text_chunk", "")[:250]
                                        dist = float(chunk.get("distance", 0))
                                        st.markdown(
                                            f'<div style="border-left:3px solid #FF6B35; padding:4px 8px; '
                                            f'margin:4px 0; font-family:\'Share Tech Mono\',monospace; '
                                            f'font-size:0.72rem; background:#F0EDE6;">'
                                            f'<b>[{i}] {src}</b> ({1-dist:.2f})<br>'
                                            f'<span style="color:#5a5450">{text}...</span>'
                                            f'</div>',
                                            unsafe_allow_html=True,
                                        )
                        with col_b:
                            if blocker_ctx:
                                with st.expander("► Blocker Context Retrieved", expanded=False):
                                    for i, chunk in enumerate(blocker_ctx, 1):
                                        src = chunk.get("module_source", "?")
                                        title = chunk.get("document_title", "?")
                                        text = chunk.get("text_chunk", "")[:250]
                                        dist = float(chunk.get("distance", 0))
                                        st.markdown(
                                            f'<div style="border-left:3px solid #cc3333; padding:4px 8px; '
                                            f'margin:4px 0; font-family:\'Share Tech Mono\',monospace; '
                                            f'font-size:0.72rem; background:#F0EDE6;">'
                                            f'<b>[{i}] {title}</b> ({1-dist:.2f})<br>'
                                            f'<span style="color:#5a5450">{text}...</span>'
                                            f'</div>',
                                            unsafe_allow_html=True,
                                        )

                        st.markdown("---")
                        st.markdown(strategic_plan)

                except Exception as exc:
                    st.error(f"Processing error: {exc}")

# ─────────────────────────────────────────────────────────────────────────
# BOTTOM PADDING (so content isn't hidden under fixed watermark bar)
# ─────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
