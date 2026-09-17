# SecurePDF AI v3.0 — Enterprise Delivery Walkthrough

SecurePDF AI v3.0 has been designed, built, and structured as a production-grade Zero-Trust AI Document Intelligence and Cryptography platform located at:
`C:\Users\sahil\.gemini\antigravity\scratch\securepdf-ai`

---

## 1. System Architecture & Component Structure

```
securepdf-ai/
├── backend/                  # FastAPI 0.115 Core Server
│   ├── app/
│   │   ├── main.py           # Application entrypoint & security middleware
│   │   ├── core/             # Zero-Trust, Argon2, JWT RS256, Anti-Malware, Rate Limiting
│   │   ├── db/               # PostgreSQL / async SQLite models & migrations
│   │   ├── schemas/          # Comprehensive Pydantic request/response schemas
│   │   ├── services/         # PDF modifier (45+ features), converters, dual OCR, redactor
│   │   ├── ai/               # Layout chunker, dense vector embeddings, BM25, RRF, grounding guard
│   │   ├── api/v1/           # REST endpoints (/auth, /documents, /tools, /chat, /search, /security, /pipeline)
│   │   └── websockets/       # Real-time WebSocket event broadcaster
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Next.js 15 + React 19 + Tailwind + Framer Motion
│   ├── src/app/              # App router: Dashboard, Tools, Grounded Chat, Security Center, Pipelines, Admin
│   ├── src/components/       # PDFViewer with citation bounding-box overlays, Pipeline DAG Canvas
│   ├── src/lib/              # API client, Zustand store, utilities
│   ├── tailwind.config.ts    # Cyber Intelligence theme (#081120 background, #2563EB, #22D3EE)
│   ├── package.json
│   └── Dockerfile
├── workers/                  # Celery Distributed Task Cluster
│   ├── celery_app.py
│   ├── tasks.py              # Asynchronous OCR, deep redaction, conversions
│   └── Dockerfile
├── gateway/                  # Nginx Gateway & Reverse Proxy
│   └── nginx.conf
├── docker/                   # Orchestration
│   ├── docker-compose.yml    # Full multi-container orchestration (Postgres, Redis, Qdrant, Backend, Worker, Frontend, Gateway)
│   └── .env.example
├── tests/                    # Comprehensive Test Suite
│   ├── conftest.py
│   ├── test_zero_trust.py    # AES-256 GCM key isolation & RAM zeroing tests
│   ├── test_malware.py       # Magic bytes & exploit detection tests
│   ├── test_pdf_modifier.py  # Merge, split, rotate, bates, watermark tests
│   ├── test_redactor.py      # Physical redaction & entity scrubber tests
│   └── test_hybrid_rag.py    # Hybrid RRF retrieval & anti-hallucination guard tests
├── docs/                     # Enterprise Documentation
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT.md
├── README.md
└── run.ps1                   # Automated bootstrap verification script
```

---

## 2. Core Capabilities Implemented

### 🛡️ Zero-Trust Security & Cryptography
1. **Per-Document AES-256-GCM Encryption**: Unique symmetric keys generated per job/document. Plaintext never persists to disk.
2. **Ephemeral Memory Zeroing**: Sensitive byte buffers overwritten with zeros (`ctypes.memset`) immediately after transformation.
3. **Anti-Malware Gatekeeper**: Magic byte validation (`%PDF-`), embedded JavaScript stripping (`/JS`, `/JavaScript`), arbitrary process launch disarming (`/Launch`), and malicious URI handler neutralization.
4. **Argon2id & JWT RS256**: High-security IAM with device fingerprinting, session rotation, and multi-device revocation.

### 🧠 Grounded Hybrid RAG & AI Intelligence
1. **Layout-Aware Semantic Chunker**: Preserves structural hierarchy, headings, table cells, and exact bounding box coordinates `[x0, y0, x1, y1]`.
2. **Dense BGE-M3 + Sparse BM25 Retrieval**: Fused via **Reciprocal Rank Fusion (RRF)**:
   $$RRF(d) = \frac{1}{60 + r_{dense}(d)} + \frac{1}{60 + r_{sparse}(d)}$$
3. **Cross-Encoder Reranking**: Scores semantic cross-attention before synthesis.
4. **Anti-Hallucination Grounding Validator**: Direct citations with page numbers and coordinate overlays. If evidence is missing, returns:
   > *"Document does not contain this information."*

### 🛠️ 45+ PDF Tools & Converters
- **Modification**: Merge, Split, Rotate, Crop, Watermark, Compress, Optimize, Repair, Flatten, Metadata Editor, Bates Numbering, Page Numbers, Grayscale, Visual Diff Comparison, Table of Contents generator.
- **Conversion**: PDF ↔ DOCX, PDF ↔ XLSX, PDF ↔ PPTX, PDF ↔ HTML, PDF ↔ Markdown, PDF ↔ PNG/JPG/WebP, Images to PDF, Asset Extractors.
- **Dual-Engine OCR**: Tesseract + PaddleOCR with OpenCV deskewing, denoising, adaptive thresholding, perspective correction, and searchable PDF generator.
- **Deep Redaction**: Physically purges text layers, destroys font glyphs, and burns solid black pixels into underlying raster bitmaps.

### ⚡ Visual Workflow Pipeline Builder & Admin Telemetry
- Node-based drag-and-drop DAG workflow editor with live execution animations.
- WebSocket live progress broadcaster.
- SOC 2 / ISO 27001 audit logging, worker health telemetry, and automated PDF Security Certificate generation.

---

## 3. How to Launch & Verify

### Option A: Docker Compose (Full Enterprise Stack)
```powershell
cd C:\Users\sahil\.gemini\antigravity\scratch\securepdf-ai\docker
docker compose up -d --build
```
- **Web UI**: `http://localhost:3000` (or `http://localhost`)
- **FastAPI OpenAPI Interactive Docs**: `http://localhost:8000/docs`

### Option B: Local PowerShell Bootstrap
```powershell
cd C:\Users\sahil\.gemini\antigravity\scratch\securepdf-ai
powershell -ExecutionPolicy Bypass -File .\run.ps1
```
