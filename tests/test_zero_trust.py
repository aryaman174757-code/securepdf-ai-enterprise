import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import pytest
from app.core.zero_trust import ZeroTrustCrypto, EphemeralWorkspace

def test_aes_gcm_encryption_roundtrip():
    key = ZeroTrustCrypto.generate_key()
    assert len(key) == 32

    plaintext = b"Enterprise Secret PDF Payload 2026"
    doc_id = "test_doc_01"

    # Encrypt
    payload, nonce = ZeroTrustCrypto.encrypt_bytes(plaintext, key, associated_data=doc_id.encode())
    assert len(payload) > len(plaintext)
    assert payload != plaintext

    # Decrypt
    decrypted = ZeroTrustCrypto.decrypt_bytes(payload, key, associated_data=doc_id.encode())
    assert decrypted == plaintext

def test_tampered_ciphertext_fails():
    key = ZeroTrustCrypto.generate_key()
    plaintext = b"Sensitive Contract Terms"
    payload, _ = ZeroTrustCrypto.encrypt_bytes(plaintext, key)

    # Tamper with byte
    tampered = bytearray(payload)
    tampered[-1] ^= 0xFF

    with pytest.raises(Exception):
        ZeroTrustCrypto.decrypt_bytes(bytes(tampered), key)

def test_memory_wiping():
    buffer = bytearray(b"SecretKeyMaterialInsideRAMBuffer")
    assert any(b != 0 for b in buffer)

    ZeroTrustCrypto.wipe_memory(buffer)
    assert all(b == 0 for b in buffer)

def test_ephemeral_workspace_lifecycle():
    with EphemeralWorkspace("session_abc", "job_123") as ws:
        test_file = ws.get_path("temp_output.pdf")
        with open(test_file, "w") as f:
            f.write("temporary data")
        assert os.path.exists(test_file)
        dir_path = ws.workspace_dir

    # Workspace directory must be destroyed upon exit
    assert not os.path.exists(dir_path)
