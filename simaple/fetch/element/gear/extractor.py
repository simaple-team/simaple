from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Dict

from pydantic import BaseModel

from simaple.fetch.element.gear.fragment import ItemFragment
from simaple.fetch.element.gear.namespace import StatType
from simaple.fetch.element.gear.provider import DomElementProvider


class PropertyExtractor(BaseModel, metaclass=ABCMeta):
    providers: Dict[str, DomElementProvider]

    @abstractmethod
    def extract(self, fragments: list[ItemFragment]):
        ...

    def _extract_from_dom_element(
        self, fragment: ItemFragment
    ) -> Dict[StatType, Dict[str, int]]:
        provider = self.providers.get(fragment.name)

        if provider is not None:
            return provider.get_value(fragment)

        return {}


class SinglePropertyExtractor(PropertyExtractor):
    target: StatType

    def extract(self, fragments: list[ItemFragment]):
        for fragment in fragments:
            provided = self._extract_from_dom_element(fragment)
            if self.target in provided:
                return {self.target: provided[self.target]}

        return {}


class ReduceExtractor(PropertyExtractor):
    def extract(self, fragments: list[ItemFragment]):
        stacks: Dict[StatType, list] = defaultdict(list)

        for fragment in fragments:
            provided = self._extract_from_dom_element(fragment)
            for k, v in provided.items():
                stacks[k].append(v)

        result = {}
        for k, list_value in stacks.items():
            contracted_value = {}
            for value in list_value:
                contracted_value.update(value)

            result[k] = contracted_value

        return result
