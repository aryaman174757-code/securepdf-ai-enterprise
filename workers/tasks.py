import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from celery_app import celery_app
from app.services.ocr_engine import ocr_service
from app.services.pdf_modifier import pdf_modifier
from app.services.redactor import redactor_service
from app.services.security_service import security_service
from app.services.storage import storage_service

@celery_app.task(bind=True, name="tasks.process_async_ocr")
def process_async_ocr(self, document_id: str, file_path: str, aes_key_hex: str, options: dict):
    """Background task for heavy OCR processing."""
    self.update_state(state="PROCESSING", meta={"progress": 10.0, "status": "Reading encrypted payload"})
    
    aes_key = bytes.fromhex(aes_key_hex)
    pdf_bytes = storage_service.retrieve_document(file_path, aes_key, document_id)
    
    self.update_state(state="PROCESSING", meta={"progress": 40.0, "status": "Executing Computer Vision Preprocessing"})
    
    ocr_res, searchable_pdf = ocr_service.run_ocr_on_pdf(
        pdf_bytes,
        language=options.get("language", "eng"),
        apply_deskew=options.get("apply_deskew", True),
        generate_searchable_pdf=True
    )
    
    self.update_state(state="PROCESSING", meta={"progress": 90.0, "status": "Finalizing Searchable PDF"})
    
    return {
        "status": "COMPLETED",
        "document_id": document_id,
        "page_count": ocr_res.page_count,
        "confidence_avg": ocr_res.confidence_avg
    }

@celery_app.task(bind=True, name="tasks.process_async_redaction")
def process_async_redaction(self, document_id: str, file_path: str, aes_key_hex: str, redactions: list):
    """Background task for deep redaction."""
    self.update_state(state="PROCESSING", meta={"progress": 20.0, "status": "Applying physical redaction"})
    
    aes_key = bytes.fromhex(aes_key_hex)
    pdf_bytes = storage_service.retrieve_document(file_path, aes_key, document_id)
    
    redacted_bytes = redactor_service.apply_deep_redaction(pdf_bytes, redactions=redactions)
    
    return {
        "status": "COMPLETED",
        "document_id": document_id,
        "output_size": len(redacted_bytes)
    }
