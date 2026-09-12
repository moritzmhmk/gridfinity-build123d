from dataclasses import dataclass


@dataclass(frozen=True)
class GridSpec:
    """Grid pitch and height unit of a Gridfinity-style system.

    `size` is the x/y grid pitch in mm, `unit` the z height unit (U).
    The defaults are the Gridfinity standard; other values produce parts
    that are self-consistent but do not interoperate with it.

    Profile dimensions (wall thickness, fillet radii, base and lip
    profiles) are absolute and do not scale with either value.
    """

    size: float = 42.0
    unit: float = 7.0


DEFAULT = GridSpec()
