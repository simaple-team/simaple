from simaple.fetch.base import MapleQuery
from simaple.fetch.query import Query, CookiedQuery, NoredirectXMLQuery
from simaple.fetch.token import TokenRepository

import pydantic

from asyncio import QueueEmpty
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib import parse

from typing import Dict


class Element:
    def run(self) -> Dict:
        query_result = self.query()
        return self.resolve(query_result)

    def query(self):
        ...

    def resolve(self):
        ...


class QueryFactory(pydantic.BaseModel):
    path: str
    name: str
    token_repository: TokenRepository

    def get_token(self) -> str:
        return self.token_repository.get(self.name)

    def get_equipments(self):
        query = CookiedQuery(
            token=self.get_token()
        )

        result = query.get()


class MapleItemListElement(Element):
    def resolve(self, text: str):
        soup = BeautifulSoup(text, 'html.parser')
        
        item_elements = soup.find(class_="item_pot").find_all("li")
        item_links = [item.find('a') for item in item_elements]
        item_urls = list(map(lambda element: element['href'] if element else '', item_links))

        return item_urls
