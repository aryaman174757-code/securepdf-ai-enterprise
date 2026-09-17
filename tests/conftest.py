import os
import io
import pytest
import fitz

# Set dev environment flag
os.environ["USE_SQLITE_DEV"] = "true"

@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generates a multi-page test PDF in memory."""
    doc = fitz.open()
    
    # Page 1
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text(fitz.Point(50, 100), "SECUREPDF AI ENTERPRISE SPECIFICATION", fontsize=16)
    p1.insert_text(fitz.Point(50, 140), "Confidential Document: All rights reserved.", fontsize=11)
    p1.insert_text(fitz.Point(50, 170), "Social Security Number: 123-45-6789 for test user John Doe.", fontsize=10)
    p1.insert_text(fitz.Point(50, 200), "Contact email: admin@securepdf.ai and telephone: (555) 019-2834.", fontsize=10)
    
    # Page 2
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text(fitz.Point(50, 100), "CHAPTER 2: ZERO-TRUST CRYPTOGRAPHY", fontsize=14)
    p2.insert_text(fitz.Point(50, 140), "Every file is encrypted with an isolated AES-256-GCM key.", fontsize=10)
    p2.insert_text(fitz.Point(50, 170), "Reciprocal rank fusion combines dense BGE-M3 and sparse BM25 scores.", fontsize=10)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

@pytest.fixture
def sample_malicious_pdf_bytes() -> bytes:
    """Generates a test PDF with simulated JavaScript stream."""
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text(fitz.Point(50, 100), "Malicious Exploit Simulation PDF")
    
    raw = doc.tobytes()
    doc.close()
    
    # Inject JavaScript and launch action markers
    raw_injected = raw + b"\n/JS (app.alert('malware_exploit'))\n/Launch /Win /F (cmd.exe)\n"
    return raw_injected
