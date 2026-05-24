from unittest.mock import MagicMock

from neko2020.application.animation_service import AnimationService
from neko2020.domain.value_objects import Point, Rect, Size

MONITOR_A = Rect(0, 0, 1920, 1080)
MONITOR_B = Rect(1920, 0, 3840, 1080)


def _make_service(monitors=None, fps=4, cursor_pos=None):
    config = MagicMock()
    config.get_int.return_value = fps

    cursor = MagicMock()
    cursor.get_cursor_position.return_value = cursor_pos or Point(960, 540)

    renderer = MagicMock()
    renderer.get_position.return_value = Point(960, 540)
    renderer.get_size.return_value = Size(32, 32)
    renderer.get_bounds.return_value = MONITOR_A

    sm = MagicMock()
    tick_result = MagicMock()
    tick_result.frame_index = 0
    tick_result.x = 960
    tick_result.y = 540
    sm.tick.return_value = tick_result

    scheduled = []

    def scheduler(delay_ms, fn):
        scheduled.append((delay_ms, fn))

    def factory():
        return sm, renderer

    svc = AnimationService(
        config=config,
        cursor=cursor,
        session_factory=factory,
        scheduler=scheduler,
        monitors=monitors or [MONITOR_A],
    )
    return svc, sm, renderer, cursor, scheduled


# ---------------------------------------------------------------------------
# _monitor_for
# ---------------------------------------------------------------------------


def test_monitor_for_cursor_in_first_monitor():
    svc, *_ = _make_service(monitors=[MONITOR_A, MONITOR_B])
    assert svc._monitor_for(Point(960, 540)) == MONITOR_A


def test_monitor_for_cursor_in_second_monitor():
    svc, *_ = _make_service(monitors=[MONITOR_A, MONITOR_B])
    assert svc._monitor_for(Point(2000, 540)) == MONITOR_B


def test_monitor_for_cursor_outside_all_falls_back_to_first():
    svc, *_ = _make_service(monitors=[MONITOR_A, MONITOR_B])
    assert svc._monitor_for(Point(-100, -100)) == MONITOR_A


def test_monitor_for_right_boundary_of_first_is_in_second():
    # MONITOR_A.right == MONITOR_B.left == 1920; right is exclusive
    svc, *_ = _make_service(monitors=[MONITOR_A, MONITOR_B])
    assert svc._monitor_for(Point(1920, 540)) == MONITOR_B


def test_monitor_for_single_monitor_always_returns_it():
    svc, *_ = _make_service(monitors=[MONITOR_A])
    assert svc._monitor_for(Point(-999, -999)) == MONITOR_A


# ---------------------------------------------------------------------------
# start / stop lifecycle
# ---------------------------------------------------------------------------


def test_start_reloads_config():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.start()
    svc._config.reload.assert_called_once()


def test_start_runs_first_tick_and_schedules_next():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.start()
    sm.tick.assert_called_once()
    renderer.render.assert_called_once_with(0, 960, 540)
    assert len(scheduled) == 1


def test_start_is_idempotent():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.start()
    svc.start()
    assert sm.tick.call_count == 1
    assert len(scheduled) == 1


def test_stop_schedules_idle_pump():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.start()
    svc.stop()
    assert len(scheduled) == 2


def test_stop_before_start_is_safe():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.stop()
    assert len(scheduled) == 0


def test_stop_is_idempotent():
    svc, sm, renderer, cursor, scheduled = _make_service()
    svc.start()
    svc.stop()
    n = len(scheduled)
    svc.stop()
    assert len(scheduled) == n


# ---------------------------------------------------------------------------
# _delay_ms
# ---------------------------------------------------------------------------


def test_delay_ms_at_4fps():
    svc, *_ = _make_service(fps=4)
    assert svc._delay_ms() == 250


def test_delay_ms_at_10fps():
    svc, *_ = _make_service(fps=10)
    assert svc._delay_ms() == 100


# ---------------------------------------------------------------------------
# Tick passes correct monitor bounds to state machine
# ---------------------------------------------------------------------------


def test_tick_passes_monitor_for_cursor_to_state_machine():
    svc, sm, renderer, cursor, _ = _make_service(
        monitors=[MONITOR_A, MONITOR_B],
        cursor_pos=Point(2000, 540),
    )
    svc.start()
    bounds_arg = sm.tick.call_args.args[3]
    assert bounds_arg == MONITOR_B


def test_tick_passes_first_monitor_when_cursor_in_it():
    svc, sm, renderer, cursor, _ = _make_service(
        monitors=[MONITOR_A, MONITOR_B],
        cursor_pos=Point(500, 300),
    )
    svc.start()
    bounds_arg = sm.tick.call_args.args[3]
    assert bounds_arg == MONITOR_A
