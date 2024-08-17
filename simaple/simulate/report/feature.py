from loguru import logger

from simaple.simulate.report.base import Report, SimulationEntry
from simaple.simulate.report.dpm import DamageCalculator


class MaximumDealingIntervalFeature:
    def __init__(self, interval: int) -> None:
        self.interval = interval

    def find_maximum_dealing_interval(
        self, report: Report, damage_calculator: DamageCalculator
    ) -> tuple[float, int, int]:
        damage_seq: list[tuple[float, float]] = []
        for entry in report.entries():
            damage_seq.append((entry.clock, damage_calculator.calculate_damage(entry)))

        best_dealing, best_start, best_end = self._find_maximum_dealing_interval(
            damage_seq
        )

        return best_dealing, best_start, best_end

    def _find_maximum_dealing_interval(
        self, damage_seq: list[tuple[float, float]]
    ) -> tuple[float, int, int]:
        # two_ptr
        start, end = 0, 0
        best_dealing: float = 0
        best_start, best_end = 0, 0

        while True:
            if end >= len(damage_seq):
                break

            if (
                end + 1 < len(damage_seq)
                and damage_seq[end + 1][0] == damage_seq[start][0]
            ):
                # Maximize interval size
                end += 1
                continue

            interval, dealing = self._compute_dealing(damage_seq, start, end)

            if interval < self.interval:
                end += 1
                continue

            if dealing > best_dealing:
                best_dealing, best_start, best_end = dealing, start, end

            start += 1

        return best_dealing, best_start, best_end

    def _compute_dealing(
        self, damage_seq: list[tuple[float, float]], start: int, end: int
    ) -> tuple[float, float]:
        start_clk = damage_seq[start][0]
        end_clk = damage_seq[end][0]
        interval = end_clk - start_clk

        if interval == 0:
            return 0, 0

        total_damage = 0.0
        for clk, damage in damage_seq[start:end]:
            total_damage += damage

        return interval, total_damage


class DamageShareFeature:
    def __init__(self, damage_calculator: DamageCalculator) -> None:
        self._damage_sum: dict[str, float] = {}
        self._damage_calculator = damage_calculator

    def update(self, entry: SimulationEntry):
        for damage_log in entry.damage_logs:
            if damage_log.name not in self._damage_sum:
                self._damage_sum[damage_log.name] = 0.0

            self._damage_sum[damage_log.name] += self._damage_calculator.get_damage(
                damage_log
            )

    def compute(self) -> dict[str, float]:
        total_damage = sum(self._damage_sum.values())
        return {
            name: damage / total_damage for name, damage in self._damage_sum.items()
        }

    def show(self):
        for name, share in sorted(
            self.compute().items(), key=lambda x: x[1], reverse=True
        ):
            logger.info(f"{share * 100:.2f} % | {name}")
