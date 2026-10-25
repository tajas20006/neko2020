from unittest.mock import MagicMock

import pytest

from neko2020.application.settings import MIN_FPS, AppSettings
from neko2020.domain.value_objects import Point

_VALUES = {
    "fps": 8,
    "duration.stop": 4,
    "duration.wash": 10,
    "duration.scratch": 4,
    "duration.yawn": 3,
    "duration.awake": 3,
    "duration.claw": 10,
    "duration.awake_rand": 20,
    "speed.max": 60,
    "idle_space": 10,
    "offset.x": 1,
    "offset.y": -35,
    "frame_hold": 2,
    "wander.sleep_time": 100,
    "wander.rand": 50,
}


def _config(**overrides):
    values = {**_VALUES, **overrides}
    config = MagicMock()
    config.get_int.side_effect = lambda path: values[path]
    config.get_string.return_value = "dog"
    config.get_bool.return_value = True
    return config


def test_from_config_maps_every_key():
    settings = AppSettings.from_config(_config())
    assert settings.fps == 8
    assert settings.animal == "dog"
    b = settings.behavior
    assert (b.stop_time, b.wash_time, b.scratch_time) == (4, 10, 4)
    assert (b.yawn_time, b.awake_time, b.claw_time) == (3, 3, 10)
    assert (b.awake_rand, b.max_speed, b.idle_space) == (20, 60, 10)
    assert b.offset == Point(1, -35)
    assert b.frame_hold == 2
    assert b.wander_enabled is True
    assert (b.wander_time, b.wander_rand) == (100, 50)


@pytest.mark.parametrize("fps", [0, -5])
def test_fps_is_floored_at_min_fps(fps):
    assert AppSettings.from_config(_config(fps=fps)).fps == MIN_FPS
