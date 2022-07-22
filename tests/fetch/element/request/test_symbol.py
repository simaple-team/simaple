import pytest

from simaple.fetch.query import CookiedQuery, NoredirectXMLQuery
from simaple.fetch.token import TokenRepository

paths = [
    "/Common/Resource/Item?p=OOGUeM7QOtPIqCEKLvIFhPSXTSGEJO02VOcWKeRzpQ7P80NNTzd0%2fhoO%2biOzCAYMj8lJneankBeCgXodpKkpDCRoL9lW9ti6If4ejKHvDDXnBt4M14GO3ZUV1yUkza4K9JgNzPH2Hs8Vf%2bTBAKF0zJubK27xH5%2fNNxBlhyqv4MUPSQ4slVkKJI6ThH6YqBNpqiGYZitJt%2bUbwzTUX4QuteraftGEPVB9U%2bTa%2bxxrun2yG9%2fq7VcUQd5FsP%2bOTQfnCKOvBTlO5cQ%2f7os1%2bvO6SHNiuzvE7u53xYoEjqX%2bGvYMTUpX0OlSaSIKi%2bWxPbGWwK4C0FnXY1nprWT07lujCYdJqL0W7e%2fEs1wwTCU51oo%3d",
    # "/Common/Resource/Item?p=OOGUeM7QOtPIqCEKLvIFhNtkXiWloWEl5ooDOQTijKP58gZ5bQW3ifqrsfsX2%2fPc299Ri0eluHxBO3kQIC%2bgobiIirlpHfGrHm0KPra5YYd73kOZVkTtM%2b4BSZUl%2fMmx7aEPbBd%2bd2U9Akw72as%2ffD7IZ%2foEDy6n%2bOz8vOnk5PW%2f8%2bdeP5D21d8cYJl0Hf%2flrLRR36n8%2bu2dcIDZSYP2gG97a1Vbf%2b1vhOqtOE3m%2b9Y5HgtL7a4HPQM92BfvTTUJ7in4mKzS2rvLnrePK6tOO%2fem6k%2bRXsBAug4Xm1MFna0b04%2bufQv0G%2fMDhkpLc4OyjZF184l9KaAlNzkjAm1VrU785hOAatrVCQ5wa5BVhLY%3d"
]


def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    result = NoredirectXMLQuery().get(paths[0], token).replace("\r\n", "\n")

    with open("tests/fetch/resources/arcane_symbol.html", "w") as f:
        f.write(result)
