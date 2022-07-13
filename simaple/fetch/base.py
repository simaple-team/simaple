from asyncio import QueueEmpty
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib import parse

from simaple.fetch.cookie import get_cookie
from bs4 import BeautifulSoup
from urllib import parse


class ResolverInterface(BaseModel):
    def resolve(self, text: str):
        ...


class MapleQuery(BaseModel):

    def get(self):
        return requests.get(self.path, headers=self.header(), allow_redirects=False)

    def header(self) -> dict:
        return {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        }


class ItemQuery(QueryInterface):
    path: str = "https://maplestory.nexon.com/Common/Character/Detail/123/Equipment"
    token: str

    def get(self):
        return requests.get(
            self.path,
            params={
                "p": self.token,
            },
            headers=self.header(),
            cookies=get_cookie(),
        )


    def header(self) -> dict:
        return {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }


class ArcaneResolver(ResolverInterface):
    def resolve(self, text: str):
        soup = BeautifulSoup(text, 'html.parser')
        
        item_links = soup.find(class_="tab03_con_wrap").find("ul").find_all('a')
        item_urls = list(map(lambda element: element['href'] if element else '', item_links))

        return item_urls


class ItemQuery(QueryInterface):
    ...

    def get(self):
        return requests.get(
            self.path,
            headers=self.header(),
            allow_redirects=False
        )

    def header(self) -> dict:
        return {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }
