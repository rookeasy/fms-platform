from pathlib import Path
from typing import BinaryIO, Protocol


class StoredFile:
    def __init__(self, *, bucket: str, key: str, path: Path, size_bytes: int) -> None:
        self.bucket = bucket
        self.key = key
        self.path = path
        self.size_bytes = size_bytes


class StorageAdapter(Protocol):
    def save(self, *, key: str, content: BinaryIO) -> StoredFile:
        ...

    def resolve_path(self, *, key: str) -> Path:
        ...
