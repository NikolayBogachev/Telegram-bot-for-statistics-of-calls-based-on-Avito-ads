
from cryptography.fernet import Fernet
import base64
import os


def generate_key() -> bytes:
    return base64.urlsafe_b64encode(os.urandom(32))


def encrypt_token(key: bytes, token: str) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(key: bytes, encrypted_token: str) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_token.encode())
    return decrypted.decode()