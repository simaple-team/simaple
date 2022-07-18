from abc import ABCMeta, abstractmethod

from pydantic import BaseModel


class Element(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def run(self, html_text):
        ...
