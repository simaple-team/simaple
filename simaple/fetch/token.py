from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib import parse


class TokenRepository:
    def __init__(self):
        self._url = 'https://maplestory.nexon.com/Ranking/World/Total'
        self._loaded_token = None
        self._any_number_for_query_detail = 0

    def get(self, name) -> str:
        if self._loaded_token is None:
            self.load(name)
        
        return self._loaded_token

    def load(self, name) -> str:
        data = requests.get(self._url, params={
            "c": name, 
            "w": self._any_number_for_query_detail
        })

        soup = BeautifulSoup(data.text, 'html.parser')
        url = soup.find(class_="search_com_chk").find("a")["href"]
        url_query = parse.urlparse(url).query
        _, pval = url_query.split("=")
        
        self._loaded_token = parse.unquote(pval)
