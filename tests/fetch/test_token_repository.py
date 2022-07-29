from simaple.fetch.token import TokenRepository


def test_pvalue_repository():
    repo = TokenRepository()
    repo.get("Backend")
