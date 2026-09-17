import os
import io
import shutil
from typing import Tuple, Optional
from app.core.config import settings
from app.core.zero_trust import ZeroTrustCrypto

class EphemeralStorageService:
    """
    Zero-Trust Encrypted Storage Service.
    All files stored on disk are encrypted using per-document unique AES-256-GCM keys.
    Plaintext never persists on physical disk.
    """

    def __init__(self):
        self.storage_root = os.path.join(settings.ZERO_TRUST_TEMP_DIR, "encrypted_store")
        os.makedirs(self.storage_root, exist_ok=True)

    def store_document(self, document_id: str, plaintext_bytes: bytes) -> Tuple[str, bytes, str]:
        """
        Encrypts plaintext with a fresh AES-256 key and persists encrypted blob.
        Returns: (encrypted_file_path, raw_aes_key, sha256_hash)
        """
        aes_key = ZeroTrustCrypto.generate_key()
        sha256_hash = ZeroTrustCrypto.compute_sha256(plaintext_bytes)
        
        # Encrypt with AES-256-GCM
        payload, nonce = ZeroTrustCrypto.encrypt_bytes(
            plaintext_bytes,
            aes_key,
            associated_data=document_id.encode()
        )
        
        file_path = os.path.join(self.storage_root, f"{document_id}.enc")
        with open(file_path, "wb") as f:
            f.write(payload)
        
        return file_path, aes_key, sha256_hash

    def retrieve_document(self, file_path: str, aes_key: bytes, document_id: str) -> bytes:
        """
        Reads encrypted blob and decrypts in memory.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("Encrypted document file not found")
        
        with open(file_path, "rb") as f:
            payload = f.read()
        
        return ZeroTrustCrypto.decrypt_bytes(
            payload,
            aes_key,
            associated_data=document_id.encode()
        )

    def delete_document(self, file_path: str):
        """Securely unlinks encrypted payload."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

storage_service = EphemeralStorageService()
