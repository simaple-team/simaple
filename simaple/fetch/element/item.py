from simaple.fetch.query import CookiedQuery

from bs4 import BeautifulSoup

from typing import Dict
from simaple.fetch.element.base import Element
from simaple.fetch.query import CookiedQuery




class ItemElement(Element):
    def fetch(self, token):
