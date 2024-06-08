from __future__ import annotations

from pathlib import Path

from simaple.core import Stat, StatProps
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.hyperstat import Hyperstat, HyperStatBasis


def _get_hyperstat_basis_from_spec() -> dict[StatProps, list[Stat]]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)

    hyperstat_basis: list[HyperStatBasis] = loader.load_all(
        query={"kind": "UpgradableUserStat"},
    )
    return {
        StatProps(basis.name): [ex_stat.stat for ex_stat in basis.values]
        for basis in hyperstat_basis
    }


_HYPERSTAT_COST = [1, 2, 4, 8, 10, 15, 20, 25, 30, 35, 50, 65, 80, 95, 110, 999999]


def get_hyperstat_lists() -> list[tuple[StatProps, list[Stat]]]:
    return list(
        sorted(_get_hyperstat_basis_from_spec().items(), key=lambda x: x[0].value)
    )


def get_empty_hyperstat_levels() -> list[int]:
    return [0 for i in range(len(_get_hyperstat_basis_from_spec()))]


def get_hyperstat_cost() -> list[int]:
    return list(_HYPERSTAT_COST)


def get_kms_hyperstat() -> Hyperstat:
    return Hyperstat(
        options=get_hyperstat_lists(),
        cost=get_hyperstat_cost(),
        levels=get_empty_hyperstat_levels(),
    )
