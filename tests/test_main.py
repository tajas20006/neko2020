import sys
from unittest.mock import MagicMock

import pytest

# pystray picks its backend at import time, which fails without a display
# (e.g. headless CI); main() is exercised with mocks anyway.
sys.modules.setdefault("pystray", MagicMock())

from neko2020 import __main__ as app  # noqa: E402
from neko2020.domain.value_objects import Point, Rect  # noqa: E402

SCREEN = Rect(-1920, 0, 1920, 1080)


@pytest.fixture
def wiring(monkeypatch):
    """Replace every Tk / Win32 / tray dependency of main() with mocks."""
    mocks = MagicMock()
    mocks.win32_overlay.get_monitors.return_value = [
        Rect(-1920, 0, 0, 1080),
        Rect(0, 0, 1920, 1080),
    ]
    mocks.win32_overlay.virtual_screen.return_value = SCREEN
    mocks.tk.Tk.return_value = mocks.root
    mocks.tk.Canvas.return_value = mocks.canvas
    mocks.pystray.Icon.return_value = mocks.tray_icon
    mocks.cursor_provider.get_cursor_position.return_value = Point(5, 6)
    mocks.TkinterCursorProvider.return_value = mocks.cursor_provider
    mocks.files.get_project_root.return_value = "/proj"
    mocks.files.get_user_config_dir.return_value = "/cfg"
    for name in (
        "win32_overlay",
        "tk",
        "pystray",
        "Image",
        "TkinterCursorProvider",
        "TkinterRenderer",
        "YamlConfigProvider",
        "AnimationService",
        "ConfigDialog",
        "NekoStateMachine",
        "files",
    ):
        monkeypatch.setattr(app, name, getattr(mocks, name))
    monkeypatch.setattr(app, "_build_state_machine", mocks.build_sm)
    return mocks


def test_create_overlay_builds_transparent_click_through_window(wiring):
    root, canvas = app._create_overlay(SCREEN)

    assert (root, canvas) == (wiring.root, wiring.canvas)
    wiring.tk.Canvas.assert_called_once_with(
        bg="green", width=3840, height=1080, highlightthickness=0
    )
    wiring.root.geometry.assert_called_once_with("3840x1080")
    wiring.root.wm_attributes.assert_any_call("-transparentcolor", "green")
    wiring.root.wm_attributes.assert_any_call("-disabled", True)
    wiring.root.after.assert_called_once_with(
        10, wiring.win32_overlay.hide_from_alt_tab, wiring.root
    )
    wiring.win32_overlay.place_window.assert_called_once_with(
        wiring.root, SCREEN
    )


def test_main_starts_service_and_runs_tray_until_mainloop_ends(wiring):
    app.main()

    service = wiring.AnimationService.return_value
    service.start.assert_called_once()
    wiring.root.mainloop.assert_called_once()
    wiring.tray_icon.run_detached.assert_called_once()
    wiring.tray_icon.stop.assert_called_once()
    wiring.AnimationService.assert_called_once()
    kwargs = wiring.AnimationService.call_args.kwargs
    assert kwargs["monitors"] == wiring.win32_overlay.get_monitors()


def test_main_session_factory_places_pet_at_cursor(wiring):
    app.main()

    factory = wiring.AnimationService.call_args.kwargs["session_factory"]
    state_machine, renderer = factory()

    assert state_machine is wiring.build_sm.return_value
    assert renderer is wiring.TkinterRenderer.return_value
    assert wiring.TkinterRenderer.call_args.args[-1] == Point(5, 6)


def test_main_scheduler_delegates_to_tk_after(wiring):
    app.main()

    scheduler = wiring.AnimationService.call_args.kwargs["scheduler"]
    callback = MagicMock()
    scheduler(40, callback)
    wiring.root.after.assert_called_with(40, callback)


def test_tray_menu_actions_run_on_the_tk_thread(wiring):
    app.main()

    items = {
        call.args[0]: call.args[1]
        for call in wiring.pystray.MenuItem.call_args_list
    }
    assert list(items) == ["Config", "Stop", "Start", "Restart", "Quit"]
    service = wiring.AnimationService.return_value
    expected = {
        "Config": wiring.ConfigDialog.return_value.open,
        "Stop": service.stop,
        "Start": service.start,
        "Restart": service.restart,
        "Quit": wiring.root.quit,
    }
    for label, action in expected.items():
        wiring.root.after.reset_mock()
        items[label](MagicMock(), MagicMock())
        wiring.root.after.assert_called_once_with(0, action)
