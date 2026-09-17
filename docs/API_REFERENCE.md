# SecurePDF AI v3.0 — OpenAPI & WebSocket Reference

Base REST URL: `/api/v1`
WebSocket Gateway: `/ws/live/{user_id}`

---

## 1. Authentication (`/auth`)

- `POST /auth/signup`: Create enterprise user account.
- `POST /auth/login`: Authenticate and obtain JWT access & refresh tokens.
- `GET /auth/me`: Get current authenticated user profile.
- `POST /auth/api-keys`: Provision new API keys (`spdf_live_...`).

---

## 2. Zero-Trust Documents (`/documents`)

- `POST /documents/upload`: Upload file with anti-malware scan and AES-256 GCM encryption.
- `GET /documents/`: List encrypted documents in active session vault.
- `GET /documents/{id}/download`: Decrypt in RAM and stream sanitized PDF.

---

## 3. PDF Modification Suite (`/tools`)

- `POST /tools/merge`: Combine multiple PDF streams.
- `POST /tools/split`: Extract page ranges (`1-3, 4-5`).
- `POST /tools/rotate`: Rotate pages by 90°, 180°, or 270°.
- `POST /tools/crop`: Crop page to `[x0, y0, x1, y1]` coordinates.
- `POST /tools/watermark`: Stamp transparent confidentiality watermark.
- `POST /tools/compress`: Downsample images and deflate streams.
- `POST /tools/bates-number`: Stamp sequential legal Bates numbering.
- `POST /tools/grayscale`: Convert color vectors to 8-bit DeviceGray.
- `POST /tools/flatten`: Flatten interactive forms and annotation layers.
- `POST /tools/compare`: Visual and textual differential comparison.

---

## 4. AI Document Chat & Search (`/chat`, `/search`)

- `POST /chat/create`: Index document structure and initialize Hybrid RAG memory.
- `POST /chat/{id}/query`: Query with strict citations, page coordinates, and anti-hallucination guard.
- `POST /search/hybrid`: Dense BGE-M3 + Sparse BM25 Reciprocal Rank Fusion search.

---

## 5. Security Center (`/security`)

- `POST /security/deep-redact`: Permanently purge font glyphs and raster pixels.
- `GET /security/scan-pii/{id}`: Scan for SSN, Credit Cards, Emails, and Phone Numbers.
- `POST /security/encrypt`: Lock PDF with AES-256 password and permission bits.
- `POST /security/sanitize-metadata`: Scrub all author, software, and XMP metadata.
- `GET /security/audit-report/{id}`: Generate formal PDF Security Audit Certificate.

---

## 6. Visual Workflow Pipelines (`/pipeline`)

- `POST /pipeline/create`: Save visual DAG workflow template.
- `GET /pipeline/templates`: Fetch enterprise pre-built workflows.
- `POST /pipeline/execute`: Run multi-step DAG pipeline with real-time status callbacks.
