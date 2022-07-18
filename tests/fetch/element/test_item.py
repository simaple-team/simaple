from simaple.fetch.element import ItemElement
from simaple.fetch.token import TokenRepository


def test_item_element():
    element = ItemElement()

    with open("tests/fetch/resources/item/16.html") as f:
        html_text = f.read()

    result = element.run(html_text)
    print(result)


"""
def test_get_item():
    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    element = ItemElement()


    for idx, path in enumerate(paths):
        if not path:
            continue

        v = element.fetch(token=token, path=path)
        v = v.replace("\r\n", "\n")
        with open(f"tests/fetch/resources/item/{idx}.html", "w") as f:
            f.write(v)
"""
