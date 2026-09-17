# SecurePDF AI v3.0 — Enterprise System Architecture

## 1. Executive Summary

SecurePDF AI v3.0 is an enterprise Zero-Trust platform engineered for highly regulated industries (Defense, Finance, Healthcare, Legal). The system guarantees:
- Ephemeral processing containment
- Multi-engine computer vision OCR
- Grounded Hybrid RAG with Reciprocal Rank Fusion
- 45+ asynchronous PDF manipulation tools
- Visual directed acyclic graph (DAG) workflow pipelines

---

## 2. Zero-Trust Cryptographic Engine

### 2.1 Per-Document Key Derivation
Every uploaded document receives a unique 256-bit AES-GCM symmetric key:
$$K_{doc} = \text{CSPRNG}(256)$$
The encrypted payload structure is packed as:
$$\text{Payload} = [\text{Nonce (12B)}] \,\|\, [\text{Ciphertext}] \,\|\, [\text{GCM Tag (16B)}]$$

### 2.2 Memory Zeroing
Upon completion of any PDF transformation, in-memory byte buffers are wiped via direct memory zeroing:
```python
ctypes.memset(ctypes.addressof(location), 0, len(byte_buffer))
```

---

## 3. Hybrid RAG & Grounded Retrieval

### 3.1 Document Chunking & Geometry
Documents are parsed into semantic chunks while preserving their exact bounding box coordinates `[x0, y0, x1, y1]`, page numbers, and structural hierarchy (headers vs paragraphs).

### 3.2 Reciprocal Rank Fusion (RRF)
Hybrid retrieval executes dense vector similarity alongside BM25 lexical token matching:
$$RRF(d) = \frac{1}{60 + r_{dense}(d)} + \frac{1}{60 + r_{sparse}(d)}$$

### 3.3 Anti-Hallucination Grounding Validator
Responses are strictly grounded in retrieved chunks. If the confidence metric falls below the threshold, the system enforces the deterministic fallback:
> *"Document does not contain this information."*

---

## 4. Visual Pipeline DAG Engine

The Visual Workflow Builder allows users to configure multi-step transformation graphs. The engine resolves dependencies via topological sorting and streams step-by-step progress over WebSockets.
