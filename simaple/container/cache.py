from abc import ABC, abstractmethod


class CharacterCache(ABC):
    @abstractmethod
    def get(self, key):
        pass

    def _compute_hash(self, x):
        ...



class LocalstorageCache():
    


