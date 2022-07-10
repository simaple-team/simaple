from pydantic import BaseModel

from abc import ABCMeta, abstractmethod

class Element(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def run(self, html_text):
        ...
