from cryptography.fernet import Fernet
from app.core.config import settings

key = settings.DB_CREDENTIAL_ENCRYPTION_KEY
fernet = Fernet(key.encode())


def encrypt_password(password: str) -> str:
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> str:
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()