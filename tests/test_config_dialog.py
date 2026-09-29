from unittest.mock import MagicMock

from neko2020.application.animation_service import MIN_FPS
from neko2020.ui.config_dialog import (
    ConfigDialog,
    _parse_int_field,
    _set_nested,
)


# ---------------------------------------------------------------------------
# _parse_int_field
# ---------------------------------------------------------------------------


def test_parse_int_field_valid_no_bounds():
    assert _parse_int_field("4", "FPS") == (4, None)


def test_parse_int_field_non_integer_returns_error():
    value, error = _parse_int_field("abc", "FPS")
    assert value is None
    assert error == "'FPS' must be an integer."


def test_parse_int_field_above_min_is_valid():
    value, error = _parse_int_field("15", "FPS", MIN_FPS)
    assert value == 15
    assert error is None


def test_parse_int_field_below_min_returns_error():
    value, error = _parse_int_field("0", "FPS", MIN_FPS)
    assert value is None
    assert error == f"'FPS' must be at least {MIN_FPS}."


def test_parse_int_field_at_min_boundary_is_valid():
    assert _parse_int_field(str(MIN_FPS), "FPS", MIN_FPS) == (MIN_FPS, None)


def test_parse_int_field_high_value_with_no_max_is_valid():
    assert _parse_int_field("1000", "FPS", MIN_FPS) == (1000, None)


# ---------------------------------------------------------------------------
# _set_nested
# ---------------------------------------------------------------------------


def test_set_nested_top_level_key():
    d: dict = {}
    _set_nested(d, "fps", 30)
    assert d == {"fps": 30}


def test_set_nested_creates_intermediate_dicts():
    d: dict = {}
    _set_nested(d, "speed.max", 60)
    assert d == {"speed": {"max": 60}}


# ---------------------------------------------------------------------------
# ConfigDialog._collect
# ---------------------------------------------------------------------------


class _FakeVar:
    def __init__(self, value: str):
        self._value = value

    def get(self) -> str:
        return self._value


def _make_dialog_with_vars(overrides: dict[str, str]):
    dialog = ConfigDialog(
        parent=MagicMock(),
        config=MagicMock(),
        user_path="/tmp/unused-config.yml",
        service=MagicMock(),
    )
    dialog._win = None
    defaults = {
        "animal": "neko",
        "speed.max": "60",
        "speed.min": "2",
        "offset.x": "0",
        "offset.y": "-35",
        "idle_space": "10",
        "duration.stop": "4",
        "duration.wash": "10",
        "duration.scratch": "4",
        "duration.yawn": "3",
        "duration.awake": "3",
        "duration.claw": "10",
        "duration.awake_rand": "20",
        "duration.walk_frame_hold": "1",
        "fps": "4",
    }
    defaults.update(overrides)
    dialog._vars = {k: _FakeVar(v) for k, v in defaults.items()}
    return dialog


def test_collect_returns_data_for_valid_values():
    dialog = _make_dialog_with_vars({})
    data = dialog._collect()
    assert data is not None
    assert data["fps"] == 4
    assert data["speed"]["max"] == 60
    assert data["animal"] == "neko"
    assert data["duration"]["walk_frame_hold"] == 1


def test_collect_allows_high_fps_with_no_upper_bound():
    dialog = _make_dialog_with_vars({"fps": "60"})
    data = dialog._collect()
    assert data is not None
    assert data["fps"] == 60


def test_collect_returns_none_for_fps_below_min(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "0"})
    shown = {}
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.showerror",
        lambda title, msg, **kw: shown.update(title=title, msg=msg),
    )
    data = dialog._collect()
    assert data is None
    assert "must be at least" in shown["msg"]


def test_collect_returns_none_for_walk_frame_hold_below_min(monkeypatch):
    dialog = _make_dialog_with_vars({"duration.walk_frame_hold": "0"})
    shown = {}
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.showerror",
        lambda title, msg, **kw: shown.update(title=title, msg=msg),
    )
    data = dialog._collect()
    assert data is None
    assert "must be at least" in shown["msg"]


def test_collect_returns_none_for_non_integer_field(monkeypatch):
    dialog = _make_dialog_with_vars({"speed.max": "not-a-number"})
    shown = {}
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.showerror",
        lambda title, msg, **kw: shown.update(title=title, msg=msg),
    )
    data = dialog._collect()
    assert data is None
    assert "must be an integer" in shown["msg"]
