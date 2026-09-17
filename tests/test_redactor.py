import sys
import os
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import pytest
from app.services.redactor import redactor_service
from app.schemas.all_schemas import RedactionItem

def test_sensitive_entity_scan(sample_pdf_bytes):
    entities = redactor_service.scan_for_sensitive_entities(sample_pdf_bytes)
    assert len(entities) > 0
    entity_types = [e["entity_type"] for e in entities]
    assert "SSN" in entity_types
    assert "EMAIL" in entity_types

def test_deep_physical_redaction(sample_pdf_bytes):
    # Apply automated SSN deep redaction
    redactions = [RedactionItem(page=1, entity_type="SSN")]
    redacted_pdf = redactor_service.apply_deep_redaction(sample_pdf_bytes, redactions=redactions)

    doc = fitz.open(stream=redacted_pdf, filetype="pdf")
    page1_text = doc[0].get_text("text")
    doc.close()

    # The SSN must be completely destroyed from text stream
    assert "123-45-6789" not in page1_text
