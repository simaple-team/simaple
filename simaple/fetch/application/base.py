from simaple.fetch.element.item import item_promise
from simaple.fetch.element.item_list import maple_item_list_promise
from simaple.fetch.token import TokenRepository


class Application:
    ...


class KMSFetchApplication(Application):
    def run(self, name: str):
        promise = maple_item_list_promise().then(
            {idx: item_promise() for idx in range(35)}
        )
        token_repository = TokenRepository()
        token = token_repository.get(name)
        result = promise.resolve("", token)
        print(result)
