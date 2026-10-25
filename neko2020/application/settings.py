from dataclasses import dataclass

from neko2020.application.ports import IConfigProvider
from neko2020.domain.settings import BehaviorSettings
from neko2020.domain.value_objects import Point

# A floor only, to avoid a ZeroDivisionError from a zero/negative fps
# in a hand-edited config.yml. Walk-cycle flicker at high fps is
# controlled separately via frame_hold.
MIN_FPS = 1


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Everything one animation session reads from the configuration."""

    fps: int
    animal: str
    behavior: BehaviorSettings

    @classmethod
    def from_config(cls, config: IConfigProvider) -> "AppSettings":
        """Read and validate the settings; the one place that knows keys."""
        return cls(
            fps=max(MIN_FPS, config.get_int("fps")),
            animal=config.get_string("animal"),
            behavior=BehaviorSettings(
                stop_time=config.get_int("duration.stop"),
                wash_time=config.get_int("duration.wash"),
                scratch_time=config.get_int("duration.scratch"),
                yawn_time=config.get_int("duration.yawn"),
                awake_time=config.get_int("duration.awake"),
                claw_time=config.get_int("duration.claw"),
                awake_rand=config.get_int("duration.awake_rand"),
                max_speed=config.get_int("speed.max"),
                idle_space=config.get_int("idle_space"),
                offset=Point(
                    config.get_int("offset.x"), config.get_int("offset.y")
                ),
                frame_hold=config.get_int("frame_hold"),
                wander_enabled=config.get_bool("wander.enabled"),
                wander_time=config.get_int("wander.sleep_time"),
                wander_rand=config.get_int("wander.rand"),
            ),
        )
