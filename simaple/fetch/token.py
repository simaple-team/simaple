from typing import cast
from urllib import parse

import requests
from bs4 import BeautifulSoup


class TokenRepository:
    def __init__(self):
        self._url = "https://maplestory.nexon.com/Ranking/World/Total"
        self._loaded_token: str = ""
        self._any_number_for_query_detail = 0

    def get(self, name: str) -> str:
        if not self._loaded_token:
            self.load(name)

        return self._loaded_token

    def load(self, name: str):
        data = requests.get(
            self._url, params={"c": name, "w": self._any_number_for_query_detail}
        )

        soup = BeautifulSoup(data.text, "html.parser")
        url = cast(str, soup.find(class_="search_com_chk").find("a")["href"])
        url_query = parse.urlparse(url).query
        _, pval = url_query.split("=")

        self._loaded_token = parse.unquote(pval)
