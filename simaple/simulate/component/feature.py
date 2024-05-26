"""
feature.py

This file contains `common` structs and classes that are used in multiple places.
"""

import pydantic


class DamageAndHit(pydantic.BaseModel):
    """
    Jointly contains damage and hit.
    """

    damage: float
    hit: float


class PeriodicFeature(pydantic.BaseModel):
    """
    Jointly contains damage and hit, interval.
    This contains information about periodic system.
    """

    damage: float
    hit: float
    interval: float
