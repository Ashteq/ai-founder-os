AI Founder OS — Privacy-First Local RAG Engine
A production-ready, enterprise-grade Executive Operating System featuring a locally hosted Retrieval-Augmented Generation (RAG) pipeline. Optimized specifically for low-latency native execution on resource-constrained edge devices (tested extensively on 8GB RAM configurations), this system handles high-throughput document ingestion, high-dimensional vector similarity indexing, and deterministic context synthesis—completely offline with zero third-party cloud data leaks.

Why This Project Hits Different
Most modern AI apps are brittle, shallow wrappers around cloud APIs that bleed subscription costs and compromise user privacy. AI Founder OS treats local LLMs as deterministic compute engines. By combining a Dockerized PostgreSQL (pgvector) instance, Ollama's compilation layer, and a reactive Streamlit frontend, this architecture provides a secure sandbox for processing sensitive startup operations: intelligent meeting analysis, compressed multi-task scheduling, strategic roadmap planning, and culture-synced hiring rubrics.

Key Engineering Milestones:
Hardware Optimized Edge Design: Orchestrates simultaneous execution of a relational database container, web servers, and deep learning model parameters within a strict 8GB RAM ceiling using Gemma 2B and Nomic-Embed-Text.

Cross-Version Resilient Infrastructure: Features custom, fail-safe API adapters to handle structural data mutations between older legacy and modern Ollama runtime engines.

Context Preservation: Implements a localized, sliding-window boundary lookback chunking algorithm preventing context fractures across data blocks.

System File Architecture
The repository follows a clean, highly modular, split-responsibility architecture separating layout rendering, persistence access, and LLM orchestration:

Plaintext
ai-founder-os/
├── app.py                 # Main Streamlit reactive UI dashboard, state router & session manager
├── database.py            # PostgreSQL relational adapter, connection pooler & pgvector interface
├── meeting_intel.py       # RAG Foundation: Sliding-window chunker & version-proof embedding helper
├── task_manager.py        # Multi-task text array aggregator & roadmap synthesizer
├── hiring_assist.py       # Cultural tensor matrix mapping, scorecard & interview metric builder
├── planner.py             # Dual-query semantic context retriever & weekly risk auditor
├── packages.txt           # Root-level Debian binary declarations (libpq-dev C-headers)
└── requirements.txt       # Pinned, environment-locked Python application dependencies
Core Pipeline & Algorithm Architectures
1. Context-Preserving Text Chunking Algorithm
Standard chunking mechanisms often slice text blindly across words, fragmenting sentences and destroying structural semantic context before vector representation. This system utilizes a deterministic sliding character window coupled with a terminal boundary scan layer.

Plaintext
[Input Raw Document String] ──► [Slide Window to Max Size (500 Chars)]
                                        │
                                        ▼
                         [Check Terminal 80-Character Buffer]
                         Does buffer contain punctuation (. ! ?)?
                                 │                │
                        (Yes) ───┘                └───► (No)
                           │                               │
                           ▼                               ▼
       Split at Last Sentence Boundary            Truncate at Max Window Size
                           │                               │
                           └───────────────┬───────────────┘
                                           ▼
                       [Strip Whitespace & Append to Chunk Array]
                                           │
                                           ▼
                  Shift Next Window Start Back by Overlap Factor (50 Chars)
Python
# Programmatic Implementation (Excerpt from meeting_intel.py)
while start < text_len:
    end = min(start + chunk_size, text_len)
    if end < text_len:
        search_region = text[max(start, end - 80): end]
        for punct in (".", "!", "?"):
            pos = search_region.rfind(punct)
            if pos != -1:
                end = max(start, end - 80) + pos + 1
                break
    chunk = text[start:end].strip()
    if chunk: chunks.append(chunk)
    start = end - overlap if end < text_len else text_len
2. The Comprehensive Local RAG Runtime Sequence
The entire document extraction, embedding vector mapping, index exploration, and contextual response generation follows a highly optimized, loop-locked runtime lifecycle.

(Similarity Score = 1 - Cosine Distance)

Plaintext
 USER RUNTIME                                    BACKEND ENGINE OPERATIONS
┌──────────────┐                                ┌──────────────────────────┐
│  Raw Input   │ ───► [ 1. Ingest Prompt ] ────►│ Check Version-Proof Abstr│
│  Text Data   │                                │ Map String to Embed-Text │
└──────────────┘                                └─────────────┬────────────┘
       ▲                                                      │ (768-Dim Dense Float Array)
       │                                                      ▼
┌──────────────┐                                ┌──────────────────────────┐
│ Markdown UI  │◄─── [ 4. Execute LLM ] ◄───────│ Query pgvector Interface │
│ Render Block │     (Gemma:2b Local Core)      │ Extract Top-K Matches    │
└──────────────┘                                └──────────────────────────┘
Orchestration Layer: User triggers compilation inside the UI. The application layer grabs unstructured payload arrays and passes them directly to the native module.

Dense Tensor Conversion: String streams flow through the embed_text wrapper, which probes the local runtime environment, sanitizes response dictionaries, and passes the output to nomic-embed-text to generate a 768-dimensional float array.

High-Dimensional Space Searching: Vector tensors execute an internal database handshake. A custom PostgreSQL driver runs a cosine distance calculation across database schemas to pinpoint the Top-K most semantically contiguous knowledge blocks.

Prompt Reconstruction & Generation: Context structures are stripped of structural padding and injected directly inside a walled-off system prompt. The final payload hits the localized Gemma 2B compiler via a native memory thread to produce deterministic markdown files.

Step-by-Step Environment Bootstrapping
To set up and run this fully containerized environment on your local Linux or WSL instance, follow these steps:

1. Spin up the Vector Database Container
Ensure Docker is installed and running, then provision your persistent vector database instance:

Bash
docker run -d \
  --name pgvector-db \
  -e POSTGRES_DB=founder_os \
  -e POSTGRES_USER=akanksha \
  -e POSTGRES_PASSWORD=secure_password_here \
  -p 5432:5432 \
  ankane/pgvector:latest
2. Initialize the Native Linux LLM Engine
In a separate terminal tab, pull down the architecture's dedicated system models using the native Linux installation layer:

Bash
# Install Ollama natively into your Linux ecosystem
curl -fsSL https://ollama.com/install.sh | sh

# Boot up the background engine service
ollama serve
Open another terminal tab and pull the pinned lightweight inference models:

Bash
ollama pull nomic-embed-text
ollama pull gemma:2b
3. Launch the Python Reactive Dashboard
Return to your project's main workspace directory, spin up your python virtual environment, satisfy dependencies, and run the server:

Bash
# Create and source local virtual environment layers
python3 -m venv venv
source venv/bin/activate

# Install native requirements
pip install -r requirements.txt

# Boot the frontend dashboard application
streamlit run app.py
