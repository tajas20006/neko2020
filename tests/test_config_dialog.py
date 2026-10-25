from unittest.mock import MagicMock

from neko2020.application.animation_service import MIN_FPS
from neko2020.ui import config_dialog
from neko2020.ui.config_dialog import (
    ConfigDialog,
    _parse_int_field,
    _scale_for_fps,
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
# _scale_for_fps
# ---------------------------------------------------------------------------


def test_scale_for_fps_scales_hold_up_and_speeds_down_together():
    data = {"frame_hold": 1, "speed": {"max": 60}}
    _scale_for_fps(data, 3.0)
    assert data == {"frame_hold": 3, "speed": {"max": 20}}


def test_scale_for_fps_floors_at_one():
    data = {"frame_hold": 3, "speed": {"max": 2}}
    _scale_for_fps(data, 10.0)
    assert data == {"frame_hold": 30, "speed": {"max": 1}}
    _scale_for_fps(data, 0.01)
    assert data["frame_hold"] == 1


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


def _make_dialog_with_vars(overrides: dict[str, str | bool], initial_fps=4):
    dialog = ConfigDialog(
        parent=MagicMock(),
        config=MagicMock(),
        service=MagicMock(),
        list_animals=lambda: [],
    )
    dialog._win = None
    dialog._initial_fps = initial_fps
    defaults = {
        "animal": "neko",
        "speed.max": "60",
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
        "wander.enabled": False,
        "wander.sleep_time": "100",
        "wander.rand": "100",
        "fps": "4",
        "frame_hold": "1",
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
    assert data["frame_hold"] == 1


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


def test_collect_returns_none_for_frame_hold_below_min(monkeypatch):
    dialog = _make_dialog_with_vars({"frame_hold": "0"})
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
    dialog._maybe_scale_for_fps(data)
    assert data["frame_hold"] == 3
    assert data["speed"] == {"max": 20}
    assert data["duration"]["stop"] == 4
    assert dialog._vars["frame_hold"].get() == "3"
    assert dialog._vars["speed.max"].get() == "20"


def test_maybe_scale_timing_leaves_data_when_user_declines(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=20)
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: False,
    )
    data = dialog._collect()
    dialog._maybe_scale_for_fps(data)
    assert data["frame_hold"] == 1
    assert data["speed"]["max"] == 60


def test_maybe_scale_timing_skips_prompt_when_fps_unchanged(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "20"}, initial_fps=20)
    asked = []
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: asked.append(True) or True,
    )
    data = dialog._collect()
    dialog._maybe_scale_for_fps(data)
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
    dialog._maybe_scale_for_fps(data)
    assert asked == []


def test_do_save_updates_initial_fps_baseline(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "60"}, initial_fps=20)
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.askyesno",
        lambda *a, **kw: True,
    )
    assert dialog._do_save() is True
    assert dialog._initial_fps == 60


def test_collect_returns_bool_for_wander_enabled():
    dialog = _make_dialog_with_vars({"wander.enabled": True})
    data = dialog._collect()
    assert data is not None
    assert data["wander"]["enabled"] is True
    assert data["wander"]["sleep_time"] == 100
    assert data["wander"]["rand"] == 100


def test_collect_returns_false_for_unchecked_wander():
    dialog = _make_dialog_with_vars({"wander.enabled": False})
    data = dialog._collect()
    assert data["wander"]["enabled"] is False


def test_open_builds_checkbox_for_bool_fields(monkeypatch):
    fake_tk = MagicMock()
    monkeypatch.setattr(config_dialog, "tk", fake_tk)
    monkeypatch.setattr(config_dialog, "ttk", MagicMock())
    config = MagicMock()
    config.get_bool.return_value = True
    config.get_string.return_value = "x"
    dialog = ConfigDialog(
        parent=MagicMock(),
        config=config,
        service=MagicMock(),
        list_animals=lambda: ["neko"],
    )
    dialog.open()
    config.get_bool.assert_called_once_with("wander.enabled")
    fake_tk.BooleanVar.assert_called_once_with(value=True)
    fake_tk.Checkbutton.assert_called_once()
    assert dialog._vars["wander.enabled"] is fake_tk.BooleanVar.return_value
    assert "wander.sleep_time" in dialog._vars


# ---------------------------------------------------------------------------
# lifecycle
# ---------------------------------------------------------------------------


def test_do_save_returns_false_when_collect_fails(monkeypatch):
    dialog = _make_dialog_with_vars({"fps": "abc"})
    monkeypatch.setattr(
        "neko2020.ui.config_dialog.messagebox.showerror",
        lambda *a, **kw: None,
    )
    assert dialog._do_save() is False


def _saved_dialog(monkeypatch):
    dialog = _make_dialog_with_vars({})
    dialog._win = MagicMock()
    return dialog


def test_save_writes_and_closes_window(monkeypatch):
    dialog = _saved_dialog(monkeypatch)
    win = dialog._win
    dialog._save()
    win.destroy.assert_called_once()
    assert dialog._win is None


def test_apply_saves_but_keeps_window_open(monkeypatch):
    dialog = _saved_dialog(monkeypatch)
    win = dialog._win
    dialog._apply()
    win.destroy.assert_not_called()
    assert dialog._win is win


def test_cancel_closes_window():
    dialog = _make_dialog_with_vars({})
    win = dialog._win = MagicMock()
    dialog._cancel()
    win.destroy.assert_called_once()
    assert dialog._win is None


def test_close_without_window_is_noop():
    dialog = _make_dialog_with_vars({})
    dialog._close()
    assert dialog._win is None


def test_open_existing_window_lifts_and_focuses():
    dialog = _make_dialog_with_vars({})
    win = dialog._win = MagicMock()
    dialog.open()
    win.lift.assert_called_once()
    win.focus_set.assert_called_once()


def test_do_save_persists_collected_data_through_config_and_restarts():
    dialog = _make_dialog_with_vars({"fps": "4"})
    assert dialog._do_save() is True
    saved = dialog._config.save.call_args.args[0]
    assert saved["fps"] == 4
    assert saved["speed"] == {"max": 60}
    dialog._service.restart.assert_called_once()


def test_open_offers_random_then_listed_animals(monkeypatch):
    fake_ttk = MagicMock()
    monkeypatch.setattr(config_dialog, "tk", MagicMock())
    monkeypatch.setattr(config_dialog, "ttk", fake_ttk)
    config = MagicMock()
    config.get_string.return_value = "neko"
    dialog = ConfigDialog(
        parent=MagicMock(),
        config=config,
        service=MagicMock(),
        list_animals=lambda: ["cat", "neko"],
    )
    dialog.open()
    values = fake_ttk.Combobox.call_args.kwargs["values"]
    assert values == ["random", "cat", "neko"]
