import os

import aiofiles
from ujson import loads


async def json_to_dict(filename: str) -> dict:
    path = f"src/data/{filename}"
    if os.path.exists(path):
        async with aiofiles.open(path, "r", encoding="utf-8") as file:
            return loads(await file.read())
    return dict()
