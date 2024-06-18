import aiofiles

from app.config.loguru_config import logger
from app.utils.clean_text import clean_text

file_cache = {}


async def read_file_async(file_path) -> str:
    if file_path in file_cache:
        return file_cache[file_path]
    try:
        async with aiofiles.open(file_path, "r") as file:
            content = clean_text(await file.read())
            file_cache[file_path] = content
            await file.close()
            return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
