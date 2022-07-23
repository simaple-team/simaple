import asyncio

from simaple.fetch.query import NoredirectXMLQuery
from simaple.fetch.token import TokenRepository

# pylint: disable=C0301


async def get_item():
    paths = [
        "/Common/Resource/Item?p=ESiGOaxye8ZazwJEjUhfLLbtbmLjtRR%2BlpFMNR04yQPrQxOiKPlxQdM/OUoW2dKzwKPZn7IWB90ONPO0sGBvD%2BXqhAcNgaTLG6MXXK8vKA67y3HFSSHe/Iq5lywPcaui/VC5ODrLMjp9iu28J3Bgk3Y4sNjzSKyjjTslTiK9YdsqcWl1oIquNZI63iFJ6is9Zc8iXpjuk/WUjibkxhxKjaN58D3AZhqmECGzWzGn0lQDl/u1O3/lgLzZ0aW0EuH/zbFvFnhw8MP2EF47ByxsOxSkTEAUg/ZheIYQjbW%2Bv7D3aEc2Oh5XScowaXuOs2Rrjk7wuBjhzmbOFgNIFc9I%2Bw%3D%3D",
        "/Common/Resource/Item?p=2NhIxJMSWOWioD3Mwz%2bZ36s%2fJl0wJ06NgwZobZ5uH41VHy6rIqHWLT8PvRdStwr0N%2f3xOxQHaSe6yQ3C%2fsNfGb0eJVl4TGf5FT783vcuB8SN31Qqhjv45bECwP2Z%2beeBCFSV8Rj7qviTK13oDTQZAXrW5mmggpdGoscA%2bgoxIt9MOUsqw1pK2faZlqNd9jAbTu2yanThL6Kz0387AZYu4o4rg%2b7TAYjbv9hHGATZTnZmAZGdH4HuFiQYzm%2fpsizjbqnVGMAuKIqYkw%2bEexBy%2fz%2b0Tb%2beawqD7czWwQBtDa3qSNdKM%2fx1LLWk9kUnuyI5ffRzllmTiZfALuDr%2bodQIQ%3d%3d",
        "/Common/Resource/Item?p=ESiGOaxye8ZazwJEjUhfLCAo546adzE56pPtINpjnpUSLNogd08IVBQKWV1OraHUFA%2bVeZK2vuY7OqXaJxJ9G3cHwPYQwH6k5%2fLDqlp4yfRF8EChAs5ZJZGgcZKex0ArchvbX2tTrUr%2byt6Vx0frRwJ6fBGXWh3tksut1HPOs9y2vch%2fbzvcCOSSHaedYMpCkdWB23GlpSB5WeomAVKfWVX9FthStU4VdlPQy7TLc8OzuK2PDhgSj2CYBcpQACIDyWsr3swpob7hZg3oD0xLZtKfZTphNDa2C3XNF86Z7cvYsuC%2bYQnueEquD108S7xVNxFXxi63pmS0a7V2KI8X3g%3d%3d",
        "/Common/Resource/Item?p=ESiGOaxye8ZazwJEjUhfLJB7QPp7rZ3CTMrS%2bF0okRGs1UppvCEsCLcFFkRg4bNRFS0YerNx3CZracxuAc0T%2fMhlx%2fW0kLbZhfc0kebwEkXQn5VQ85EBxGzexCviNdFcP6E5Uw3Wlm1F5wLaOe1BOe0ENos986sNZnGBvfyB7f3Jgi%2f27EJnqmWqKD%2bTP9qiU2oL%2bZamdNi3nkucexk%2bqVULRZPbT%2bNFFCEDxdB1xWRsSGmmkOFb4Zry7Vn7infUYVw%2f20G4%2flPpW9me0ofbRh2Edd0wg9WYo34Jt7UPf5SJoy6phGLb9WJW2avRlReANBg6UmhFVqCJdFQhHC08mg%3d%3d",
        "/Common/Resource/Item?p=ESiGOaxye8ZazwJEjUhfLF5aZS1g1J8TPN7KJ8GhGm5uHyC0s0%2bDRnAEHNEzcJLaJj3sLSfnP1MdFj05QsyYI56%2b6GTaWugJ4vAAoW3FxbsRn8kMmgjKLFGmu9gdnIBAwMhhl41r4GCPwkB2DEYEJO12kQw0ut3U6pv8043vfZdE1kRjKnzgJxKxFB%2bChP69Lcnh2TbC%2bw89MFzE2pTsck%2b3X7N%2bKsNxKKCdA4E%2bvf7LdyQMsiii79y3h97EViTEpqicmZ5sAZI2rUJmAOWyt2zZvsmMDrbiLjQFSD9Sm3qCyhcdxynLhpxI5CEq3S0SNZMD0BQzU6hJQC3rA7dB9g%3d%3d",
        "/Common/Resource/Item?p=2NhIxJMSWOWioD3Mwz%2bZ3yY0ye5i5zG87mN1pbmH6Ni89aoi7ar7pl%2fwPDvH89pAq2jaTXYJJnzmcF%2by4DE374TfTbQO5JxJj6MhuY%2bP5Sldnci82KGZKuHDk6aNjYHj26%2fhoc1JweevPXUwcDpPBI1umOqTud6bwLJz91hc8q3flNUBNBlbdJ32Ax0bTcGk0vJ1hDYZwy%2fXzLILrWgAvNJT5kP%2bL3UTnrdLERqF0skUD1Au%2bV1A%2bwfdGpDD5GAg5YfG0T7rG9oTVM66SFmYLEbY1O5EuRYCn9Ffjgrl%2bVd9czNFuDII5ME2uJhUuo%2bfditSnsYTaob4%2bteGTrvJew%3d%3d",
        "/Common/Resource/Item?p=ESiGOaxye8ZazwJEjUhfLH84sLdo2Mvlqlziub5O8U8rKgMN4gcMlwx2nzENhYNxMQnLgFdQqt4DiuyHbRhqU0p1Tfpe6Ma0tX4duxFZ4oJz1KMkh8zLB2RHRVoh%2bMQKtHqp2hcdIlplZ4DWC7PNrICxNDDUHbXES3cH4rgsZ0uv5ifqZyoe4E83JYkqy%2fJOQhsAVnWb3Sx5%2fnKsdxdMDKNkVsy2KQvDzJmRnh4e1szJa7hY4Ael61zVDLlMSniol75oiflLCr9EjCd9R18Fx%2fQF9xe4NRR1MYK16G5WQ1rKdWnp74Khh6pEq7wGMMDb8N6BYBlUF2%2bpYNgbRgV4xw%3d%3d",
    ]

    token_repository = TokenRepository()
    name = "Backend"
    token = token_repository.get(name)

    for path in paths:
        result = await NoredirectXMLQuery().get(path, token)


def test():
    asyncio.run(get_item())
