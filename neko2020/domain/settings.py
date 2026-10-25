from dataclasses import dataclass

from neko2020.domain.value_objects import Point


@dataclass(frozen=True, slots=True)
class BehaviorSettings:
    """Tunables of the pet's behavior; durations count sprite swaps."""

    stop_time: int
    wash_time: int
    scratch_time: int
    yawn_time: int
    awake_time: int
    claw_time: int
    awake_rand: int
    max_speed: int
    idle_space: int
    offset: Point
    frame_hold: int
    wander_enabled: bool = False
    wander_time: int = 100
    wander_rand: int = 100
