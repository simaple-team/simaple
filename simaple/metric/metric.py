from abc import ABCMeta
from typing import List

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

from simaple.core.base import Stat
from simaple.job.job import Job


class Metric(metaclass=ABCMeta):
    def evaluate(self, stat: Stat) -> float:
        ...


class RegressionMetric(Metric):
    def __init__(self, job: Job, degree: int = 3):
        self.job = job
        self._references: List[Stat] = []
        self.degree = degree

    def add_reference(self, stat: Stat):
        self._references.append(stat)

    def _create_model(self, x: List[float], y: List[float]):
        x_train = np.array(x)[:, np.newaxis]
        y_train = np.array(y)

        model = make_pipeline(PolynomialFeatures(self.degree), Ridge(alpha=1e-3))
        model.fit(x_train, y_train)
        return model

    def _get_score(self, stat: Stat) -> float:
        return self.job.damage_logic.get_major_stat(stat + self.job.get_default_stat())

    def _get_scale(self, stat: Stat) -> float:
        return (
            self.job.damage_logic.get_damage_factor(stat + self.job.get_default_stat())
            / 1e9
        )

    def evaluate(self, stat: Stat) -> float:
        scales = [self._get_scale(ref_stat) for ref_stat in self._references]
        scores = [self._get_score(ref_stat) for ref_stat in self._references]

        model = self._create_model(scales, scores)

        target_x = self._get_scale(stat)
        target_y = model.predict([[target_x]])

        return target_y[0]
