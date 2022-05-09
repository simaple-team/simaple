import itertools
from typing import Any, Iterable


class Iterator:
    def single_iterator(self, length: int):
        for i in range(length):
            yield (i,)

    def double_iterator(self, length: int):
        for i in range(length):
            yield (i, i)

        for v in itertools.combinations(range(length), 2):
            yield v

    def triple_iterator(self, length: int):
        for i in range(length):
            yield (i, i, i)

        for i, j in itertools.permutations(range(length), 2):
            yield (i, i, j)

        for v in itertools.combinations(range(length), 3):
            yield v

    def quadruple_iterator(self, length: int):
        for i in range(length):
            yield (i, i, i, i)

        for i, j in itertools.permutations(range(length), 2):
            yield (i, i, i, j)

        for i, j in itertools.combinations(range(length), 2):
            yield (i, i, j, j)

        for i in range(length):
            for j, k in itertools.combinations(
                [idx for idx in range(length) if idx != i], 2
            ):
                yield (i, i, j, k)

        for v in itertools.combinations(range(length), 4):
            yield v

    def cumulated_iterator(self, length: int, maximum_depth: int) -> Iterable[Any]:
        if maximum_depth >= 1:
            for v in self.single_iterator(length):
                yield v
        if maximum_depth >= 2:
            for v in self.double_iterator(length):
                yield v
        if maximum_depth >= 3:
            for v in self.triple_iterator(length):
                yield v
        if maximum_depth >= 4:
            for v in self.quadruple_iterator(length):
                yield v
