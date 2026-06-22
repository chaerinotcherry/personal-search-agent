from auth.config import ENCRYPTION_KEY
from cryptography.fernet import Fernet

fernet = Fernet(ENCRYPTION_KEY.encode() if ENCRYPTION_KEY else Fernet.generate_key())


def encrypt(plain: str) -> str:
    return fernet.encrypt(plain.encode()).decode()


def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
