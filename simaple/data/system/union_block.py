from pathlib import Path

from simaple.core import JobType
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.union import UnionBlock, UnionSquad


def get_all_blocks() -> list[UnionBlock]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)

    return loader.load_all(
        query={"kind": "UnionBlock"},
    )


def create_with_some_large_blocks(
    large_block_jobs: list[JobType], default_size: int = 4, large_size: int = 5
) -> UnionSquad:
    blocks = get_all_blocks()
    size = [
        (large_size if block.job in large_block_jobs else default_size)
        for block in blocks
    ]
    return UnionSquad(blocks=blocks, block_size=size)
