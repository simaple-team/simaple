import asyncio
import json
from abc import ABCMeta, abstractmethod

import aiohttp
from loguru import logger
from pydantic import BaseModel

from simaple.fetch.cookie import get_cookie


class Query(BaseModel, metaclass=ABCMeta):
    def url(self, path) -> str:
        if path[0] == "/":
            path = path[1:]
        return f"https://maplestory.nexon.com/{path}"

    @abstractmethod
    async def get(self, path, token) -> str:
        ...


class CookiedQuery(Query):
    max_retry: int = 5
    retry_await: float = 0.5

    async def get(self, path, token) -> str:
        header = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        }
        logger.info(f"Request to {self.url}")

        async with aiohttp.ClientSession() as session:
            for _ in range(self.max_retry):
                response = await session.get(
                    self.url(path),
                    params={
                        "p": token,
                    },
                    headers=header,
                    cookies=get_cookie(),
                )
                text = await response.text()
                if len(text) == 0:
                    logger.info(f"Retry {path}")
                    await asyncio.sleep(self.retry_await)
                    continue

                return text

        raise ConnectionRefusedError("Connection Refused from homepage")


class NoredirectXMLQuery(Query):
    max_retry: int = 5
    retry_await: float = 0.5

    async def get(self, path, token) -> str:
        header = {
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }
        logger.info(f"Request to {self.url(path)}")

        async with aiohttp.ClientSession() as session:
            for _ in range(self.max_retry):
                response = await session.get(
                    self.url(path), headers=header, allow_redirects=False
                )
                raw_text = await response.text()
                if len(raw_text) == 0:
                    logger.info(f"Retry {path}")
                    await asyncio.sleep(self.retry_await)
                    continue

                text: str = json.loads(raw_text)["view"].replace("\r\n", "\n")
                if len(text) == 0:
                    logger.info(f"Retry {path}")
                    await asyncio.sleep(self.retry_await)
                    continue

                return text

        raise ConnectionRefusedError("Connection Refused from homepage")
