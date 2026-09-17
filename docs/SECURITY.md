# SecurePDF AI v3.0 — Enterprise Security Specification

## 1. Zero-Trust Security Guarantees

SecurePDF AI operates under a Zero-Trust architecture:
- **No Plaintext Persistence**: Document bytes are immediately encrypted with AES-256-GCM.
- **Isolated Workspaces**: Temporary folders are created per-job and securely wiped upon exit.
- **Anti-Malware Gatekeeper**: Magic byte checks and PDF AST stream sanitization neutralize `/JavaScript`, `/Launch`, and malicious URI schemes before file parsing.

## 2. Authentication & Authorization

- **Argon2id Hashing**: Password hashing with 64MB memory cost, 3 time iterations, and 4 parallel threads.
- **JWT RS256/HS256**: Short-lived access tokens (120 mins) with device fingerprint validation.
- **Session Revocation**: Real-time multi-device session revocation via JTI token tracking.

## 3. Deep Physical Redaction vs Visual Overlays

| Feature | Standard PDF Editor | SecurePDF AI v3.0 |
| :--- | :--- | :--- |
| **Visual Black Box** | Yes | Yes |
| **Text Layer Purge** | No (Forensically Recoverable) | **Yes (Destroyed)** |
| **Font Glyph Elimination** | No | **Yes (Purged from PDF table)** |
| **Raster Pixel Burn-In** | No | **Yes (Overwritten with solid black)** |
| **Metadata & XMP Scrub** | Partial | **Complete Purge** |
