from simaple.fetch.element import CharacterElement


def test_item_element():
    element = CharacterElement()

    with open("tests/fetch/resources/character.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    #  print(result)
