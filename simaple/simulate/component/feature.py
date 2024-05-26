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
