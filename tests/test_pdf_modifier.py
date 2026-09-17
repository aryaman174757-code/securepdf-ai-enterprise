import sys
import os
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import pytest
from app.services.pdf_modifier import pdf_modifier

def test_pdf_merge(sample_pdf_bytes):
    merged = pdf_modifier.merge_pdfs([sample_pdf_bytes, sample_pdf_bytes])
    doc = fitz.open(stream=merged, filetype="pdf")
    assert len(doc) == 4
    doc.close()

def test_pdf_split(sample_pdf_bytes):
    splits = pdf_modifier.split_pdf(sample_pdf_bytes, ["1", "2"])
    assert len(splits) == 2
    
    doc1 = fitz.open(stream=splits[0], filetype="pdf")
    assert len(doc1) == 1
    doc1.close()

def test_pdf_rotation(sample_pdf_bytes):
    rotated = pdf_modifier.rotate_pdf(sample_pdf_bytes, 90, [1])
    doc = fitz.open(stream=rotated, filetype="pdf")
    assert doc[0].rotation == 90
    doc.close()

def test_pdf_watermark(sample_pdf_bytes):
    watermarked = pdf_modifier.add_watermark(sample_pdf_bytes, text="CONFIDENTIAL-AUDIT")
    assert len(watermarked) > 0
    doc = fitz.open(stream=watermarked, filetype="pdf")
    assert len(doc) == 2
    doc.close()

def test_bates_numbering(sample_pdf_bytes):
    bates_pdf = pdf_modifier.bates_number_pdf(sample_pdf_bytes, prefix="CASE-", start_number=500)
    doc = fitz.open(stream=bates_pdf, filetype="pdf")
    assert "CASE-000500" in doc[0].get_text("text")
    assert "CASE-000501" in doc[1].get_text("text")
    doc.close()

def test_grayscale_conversion(sample_pdf_bytes):
    gray = pdf_modifier.convert_to_grayscale(sample_pdf_bytes)
    assert len(gray) > 0
