from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.storage.base import StoredFile


class LocalStorageAdapter:
    def __init__(self, root: str, bucket: str) -> None:
        self.root = Path(root)
        self.bucket = bucket

    def save(self, *, key: str, content: BinaryIO) -> StoredFile:
        path = self.resolve_path(key=key)
        path.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        with path.open("wb") as target:
            while chunk := content.read(1024 * 1024):
                size += len(chunk)
                target.write(chunk)
        return StoredFile(bucket=self.bucket, key=key, path=path, size_bytes=size)

    def resolve_path(self, *, key: str) -> Path:
        root = self.root.resolve()
        path = (root / key).resolve()
        if root not in path.parents and path != root:
            raise ValueError("Storage key resolves outside configured local storage root.")
        return path


local_storage = LocalStorageAdapter(root=settings.upload_root, bucket=settings.storage_bucket)
