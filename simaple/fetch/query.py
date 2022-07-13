from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib import parse

from simaple.fetch.cookie import get_cookie
from bs4 import BeautifulSoup
from urllib import parse
import json

class Query(BaseModel):
    path: str

    @property
    def url(self) -> str:
        return f"https://maplestory.nexon.com/{self.path}"

    def get(self) -> str:
        ...


class CookiedQuery(Query):
    token: str

    def get(self) -> str:
        header = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }

        return requests.get(
            self.url,
            params={
                "p": self.token,
            },
            headers=header,
            cookies=get_cookie(),
        ).text


class NoredirectXMLQuery(Query):
    token: str
    path: str

    def get(self):
        header = {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        response = requests.get(
            self.url,
            headers=header,
            allow_redirects=False
        )
        text = json.loads(response.text)["view"]
        return text