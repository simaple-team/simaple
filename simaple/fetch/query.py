import json
from abc import ABCMeta, abstractmethod

import requests
from loguru import logger
from pydantic import BaseModel

from simaple.fetch.cookie import get_cookie


class Query(BaseModel, metaclass=ABCMeta):
    def url(self, path) -> str:
        if path[0] == "/":
            path = path[1:]
        return f"https://maplestory.nexon.com/{path}"

    @abstractmethod
    def get(self, path, token) -> str:
        ...


class CookiedQuery(Query):
    def get(self, path, token) -> str:
        header = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        }
        logger.info(f"Request to {self.url}")
        return requests.get(
            self.url(path),
            params={
                "p": token,
            },
            headers=header,
            cookies=get_cookie(),
        ).text


class NoredirectXMLQuery(Query):
    def get(self, path, token) -> str:
        header = {
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }
        logger.info(f"Request to {self.url(path)}")
        response = requests.get(self.url(path), headers=header, allow_redirects=False)
        text = json.loads(response.text)["view"].replace("\r\n", "\n")
        return text
