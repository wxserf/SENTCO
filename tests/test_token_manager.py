from pathlib import Path

from cryptography.fernet import Fernet

from sentience.utils.token_manager import SecureTokenManager


def test_token_round_trip(tmp_path: Path) -> None:
    key = Fernet.generate_key().decode()
    manager = SecureTokenManager(key, token_dir=tmp_path)
    manager.save_token("123", "secret")
    assert (tmp_path / "123.token").exists()
    assert manager.load_token("123") == "secret"


def test_token_wrong_key(tmp_path: Path) -> None:
    key = Fernet.generate_key().decode()
    manager = SecureTokenManager(key, token_dir=tmp_path)
    manager.save_token("abc", "value")

    other = SecureTokenManager(Fernet.generate_key().decode(), token_dir=tmp_path)
    assert other.load_token("abc") is None
