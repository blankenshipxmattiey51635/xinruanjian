"""Encrypted local storage for API keys and other secrets."""
from __future__ import annotations

import json
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from app.utils.paths import ensure_runtime_dirs


class SecureStore:
    """Store provider API keys encrypted with a local machine file key."""

    def __init__(self, key_path: Path | None = None, data_path: Path | None = None) -> None:
        dirs = ensure_runtime_dirs()
        self.key_path = key_path or dirs["config"] / ".secret.key"
        self.data_path = data_path or dirs["config"] / "api_keys.enc"
        self._fernet = Fernet(self._load_or_create_key())

    def set_secret(self, provider: str, secret: str) -> None:
        data = self._load_all()
        data[provider] = secret
        self._save_all(data)

    def get_secret(self, provider: str) -> str:
        return self._load_all().get(provider, "")

    def providers(self) -> list[str]:
        return sorted(self._load_all().keys())

    def _load_or_create_key(self) -> bytes:
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        if self.key_path.exists():
            return self.key_path.read_bytes()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _load_all(self) -> dict[str, str]:
        if not self.data_path.exists():
            return {}
        try:
            payload = self._fernet.decrypt(self.data_path.read_bytes())
        except InvalidToken:
            return {}
        return json.loads(payload.decode("utf-8"))

    def _save_all(self, data: dict[str, str]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.data_path.write_bytes(self._fernet.encrypt(payload))
