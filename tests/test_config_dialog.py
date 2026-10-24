from unittest.mock import MagicMock

from neko2020.application.animation_service import MIN_FPS
from neko2020.ui.config_dialog import (
    ConfigDialog,
    _parse_int_field,
    _scale_durations,
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
# _scale_durations
# ---------------------------------------------------------------------------


def test_scale_durations_multiplies_by_ratio():
    result = _scale_durations({"walk_frame_hold": 1, "stop": 4}, 3.0)
    assert result == {"walk_frame_hold": 3, "stop": 12}


def test_scale_durations_rounds_to_nearest_int():
    result = _scale_durations({"stop": 5}, 1.5)
    assert result == {"stop": 8}  # round(7.5) == 8 (banker's rounding)


def test_scale_durations_floors_at_one():
    result = _scale_durations({"walk_frame_hold": 3}, 0.1)
    assert result == {"walk_frame_hold": 1}


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

    def set(self, value: str) -> None:
        self._value = value


def _make_dialog_with_vars(overrides: dict[str, str], initial_fps=4):
    dialog = ConfigDialog(
        parent=MagicMock(),
        config=MagicMock(),
        user_path="/tmp/unused-config.yml",
        service=MagicMock(),
    )
    dialog._win = None
    dialog._initial_fps = initial_fps
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


# ---------------------------------------------------------------------------
# ConfigDialog._maybe_scale_timing
# ---------------------------------------------------------------------------


def test_maybe_scale_timing_scales_when_user_confirms(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=20)
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: True,
    )
    data = dialog._collect()
    dialog._maybe_scale_timing(data)
    assert data["duration"]["walk_frame_hold"] == 3
    assert data["duration"]["stop"] == 12
    assert dialog._vars["duration.walk_frame_hold"].get() == "3"


def test_maybe_scale_timing_leaves_data_when_user_declines(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=20)
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: False,
    )
    data = dialog._collect()
    dialog._maybe_scale_timing(data)
    assert data["duration"]["walk_frame_hold"] == 1
    assert data["duration"]["stop"] == 4


def test_maybe_scale_timing_skips_prompt_when_fps_unchanged(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "20"}, initial_fps=20)
    asked = []
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: asked.append(True) or True,
    )
    data = dialog._collect()
    dialog._maybe_scale_timing(data)
    assert asked == []
    assert data["duration"]["stop"] == 4


def test_maybe_scale_timing_skips_prompt_when_no_initial_fps(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=None)
    asked = []
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: asked.append(True) or True,
    )
    data = dialog._collect()
    dialog._maybe_scale_timing(data)
    assert asked == []


def test_do_save_updates_initial_fps_baseline(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=20)
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: True,
    )
    monkeypatch.setattr(
        "neko2020.ui.config_dialog._write_config", lambda *a, **kw: None
    )
    assert dialog._do_save() is True
    assert dialog._initial_fps == 60
