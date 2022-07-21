from simaple.fetch.element import CharacterElement
from simaple.fetch.token import TokenRepository


def test_item_element():
    element = CharacterElement()

    with open("tests/fetch/resources/character.html") as f:
        html_text = f.read()

    result = element.run(html_text)
    #  print(result)
