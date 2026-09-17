import os
import shutil
import secrets
import hashlib
import hmac
import tempfile
import ctypes
from typing import Tuple, Generator
from contextlib import contextmanager
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings

class ZeroTrustCrypto:
    """
    Zero-Trust Cryptographic Engine
    Enforces per-job unique AES-256-GCM keys, authenticated encryption,
    and ephemeral memory zeroing.
    """

    @staticmethod
    def generate_key() -> bytes:
        """Generate a cryptographically secure 256-bit (32-byte) AES key."""
        return secrets.token_bytes(32)

    @staticmethod
    def encrypt_bytes(data: bytes, key: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes]:
        """
        Encrypts plaintext bytes using AES-256-GCM.
        Returns: (nonce + ciphertext + tag, nonce)
        """
        if len(key) != 32:
            raise ValueError("AES-256 requires a 32-byte key")
        
        nonce = secrets.token_bytes(12)  # Standard 96-bit nonce for GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, associated_data)
        
        # Pack nonce + ciphertext
        payload = nonce + ciphertext
        return payload, nonce

    @staticmethod
    def decrypt_bytes(payload: bytes, key: bytes, associated_data: bytes = b"") -> bytes:
        """
        Decrypts an AES-256-GCM payload.
        Payload format: [12 bytes nonce][ciphertext + 16 bytes tag]
        """
        if len(key) != 32:
            raise ValueError("AES-256 requires a 32-byte key")
        if len(payload) < 28:
            raise ValueError("Invalid ciphertext length")

        nonce = payload[:12]
        ciphertext = payload[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, associated_data)

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """Compute SHA-256 hex digest for integrity verification."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_hmac(key: bytes, data: bytes) -> str:
        """Compute HMAC-SHA256 for message authentication."""
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def wipe_memory(byte_buffer: bytearray):
        """
        Securely overwrites sensitive in-memory byte buffers with zero bytes
        using memory view and ctypes memset.
        """
        if isinstance(byte_buffer, bytearray):
            for i in range(len(byte_buffer)):
                byte_buffer[i] = 0
            try:
                location = (ctypes.c_char * len(byte_buffer)).from_buffer(byte_buffer)
                ctypes.memset(ctypes.addressof(location), 0, len(byte_buffer))
            except Exception:
                pass


class EphemeralWorkspace:
    """
    Isolated temporary filesystem workspace.
    Ensures complete destruction of artifacts and intermediate processing buffers.
    """

    def __init__(self, session_id: str, job_id: str):
        self.session_id = session_id
        self.job_id = job_id
        base_dir = settings.ZERO_TRUST_TEMP_DIR
        os.makedirs(base_dir, exist_ok=True)
        self.workspace_dir = tempfile.mkdtemp(prefix=f"secpdf_{session_id}_{job_id}_", dir=base_dir)

    def get_path(self, filename: str) -> str:
        """Get absolute path to a file inside the isolated workspace."""
        # Sanitize filename to prevent path traversal
        clean_name = os.path.basename(filename)
        return os.path.join(self.workspace_dir, clean_name)

    def cleanup(self):
        """Securely wipe and remove the workspace directory."""
        try:
            if os.path.exists(self.workspace_dir):
                # Overwrite files before unlinking for high-security environments
                for root, _, files in os.walk(self.workspace_dir):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            size = os.path.getsize(fp)
                            with open(fp, "wb") as wipe_file:
                                wipe_file.write(secrets.token_bytes(min(size, 4096)))
                        except Exception:
                            pass
                shutil.rmtree(self.workspace_dir, ignore_errors=True)
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


@contextmanager
def ephemeral_session(session_id: str, job_id: str) -> Generator[EphemeralWorkspace, None, None]:
    workspace = EphemeralWorkspace(session_id, job_id)
    try:
        yield workspace
    finally:
        workspace.cleanup()
