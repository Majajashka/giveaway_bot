from io import BytesIO

import aiofiles
import asyncio
from pathlib import Path


class MediaStorage:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._lock = asyncio.Lock()

    async def save_media(self, media_data: bytes, filename: str) -> None:
        file_path = self.storage_path / filename
        async with self._lock:
            async with aiofiles.open(file_path, 'wb') as file:
                await file.write(media_data)

    async def get_media(self, filename: str) -> BytesIO:
        file_path = self.storage_path / filename
        async with self._lock:
            async with aiofiles.open(file_path, 'rb') as file:
                data = await file.read()
        return BytesIO(data)
