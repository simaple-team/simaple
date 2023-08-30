from typing import Union, cast
from urllib import parse

import requests
from bs4 import BeautifulSoup


class TokenRepository:
    def __init__(self, reboot: bool = False) -> None:
        self._url = "https://maplestory.nexon.com/Ranking/World/Total"
        self._loaded_token: str = ""
        self._reboot = reboot

    def get(self, name: str) -> str:
        if not self._loaded_token:
            self.load(name)

        return self._loaded_token

    def load(self, name: str) -> None:
        params: dict[str, Union[str, int]] = {
            "c": name,
            "w": 254 if self._reboot else 0,
        }

        data = requests.get(self._url, params=params)

        soup = BeautifulSoup(data.text, "html.parser")
        url = cast(str, soup.find(class_="search_com_chk").find("a")["href"])
        url_query = parse.urlparse(url).query
        _, pval = url_query.split("=")

        self._loaded_token = parse.unquote(pval)
