import aiofiles
import httpx
import redis
import os
from dotenv import load_dotenv

import config

load_dotenv()

def get_redis_client():
    return redis.Redis.from_url(config.Config.REDIS_URL)


async def save_image(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        image_data = response.content

    image_path = os.path.join("images", os.path.basename(url))
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    async with aiofiles.open(image_path, "wb") as file:
        await file.write(image_data)

    return image_path
