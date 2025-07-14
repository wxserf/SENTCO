import logging
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecureTokenManager:
    """Encrypt and store refresh tokens using Fernet."""

    def __init__(self, key: str, token_dir: Path = Path("tokens")) -> None:
        self.fernet = Fernet(key)
        self.token_dir = token_dir
        self.token_dir.mkdir(exist_ok=True)

    def save_token(self, identifier: str, token: str) -> None:
        """Encrypt and save a refresh token."""
        token_path = self.token_dir / f"{identifier}.token"
        encrypted = self.fernet.encrypt(token.encode())
        with open(token_path, "wb") as f:
            f.write(encrypted)

    def load_token(self, identifier: str) -> Optional[str]:
        """Load and decrypt a refresh token."""
        token_path = self.token_dir / f"{identifier}.token"
        if not token_path.exists():
            return None

        try:
            encrypted = token_path.read_bytes()
            return self.fernet.decrypt(encrypted).decode()
        except Exception as exc:  # broad catch to avoid failing on corrupt token
            logger.error("Failed to decrypt token %s: %s", identifier, exc)
            return None
