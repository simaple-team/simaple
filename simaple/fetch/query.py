from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib import parse

from simaple.fetch.cookie import get_cookie
from bs4 import BeautifulSoup
from urllib import parse


class Query(BaseModel):
    path: str

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
            self.path,
            params={
                "p": self.token,
            },
            headers=header,
            cookies=get_cookie(),
        ).text


class NoredirectXMLQuery(Query):
    def get(self):
        header = {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }

        return requests.get(
            self.path,
            headers=header,
            allow_redirects=False
        )
