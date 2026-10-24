import pytest

from neko2020.domain.state_machine import NekoStateMachine, State
from neko2020.domain.value_objects import Point, Rect, Size

BOUNDS = Rect(0, 0, 1920, 1080)
SIZE = Size(32, 32)
CENTER = Point(960, 540)


def make_sm(**overrides):
    defaults = dict(
        stop_time=4,
        wash_time=10,
        scratch_time=4,
        yawn_time=3,
        awake_time=3,
        claw_time=10,
        awake_rand=0,
        min_speed=2,
        max_speed=60,
        idle_space=10,
        offset=Point(0, 0),
    )
    defaults.update(overrides)
    return NekoStateMachine(**defaults)


def tick_n(sm, n, cursor, position=CENTER):
    result = None
    for _ in range(n):
        result = sm.tick(cursor, position, SIZE, BOUNDS)
    return result


# ---------------------------------------------------------------------------
# _calc_direction: 8 octants + zero-vector
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dx, dy, expected",
    [
        (10, 0, State.R_MOVE),
        (5, -5, State.UR_MOVE),
        (1, -10, State.U_MOVE),
        (5, 5, State.DR_MOVE),
        (1, 10, State.D_MOVE),
        (-10, 0, State.L_MOVE),
        (-5, -5, State.UL_MOVE),
        (-5, 5, State.DL_MOVE),
        (-1, 10, State.D_MOVE),
        (0, 0, State.STOP),
    ],
)
def test_calc_direction(dx, dy, expected):
    sm = make_sm()
    sm.dx = dx
    sm.dy = dy
    sm._calc_direction()
    assert sm.state == expected


# ---------------------------------------------------------------------------
# _set_new_state
# ---------------------------------------------------------------------------


def test_set_new_state_resets_counters_on_change():
    sm = make_sm()
    sm.tick_count = 3
    sm.state_count = 5
    sm._set_new_state(State.WASH)
    assert sm.state == State.WASH
    assert sm.tick_count == 0
    assert sm.state_count == 0


def test_set_new_state_no_reset_for_same_state():
    sm = make_sm()
    sm.tick_count = 3
    sm.state_count = 5
    sm.state = State.STOP
    sm._set_new_state(State.STOP)
    assert sm.tick_count == 3
    assert sm.state_count == 5


# ---------------------------------------------------------------------------
# _move_start
# ---------------------------------------------------------------------------


def test_move_start_true_on_horizontal_right_jump():
    sm = make_sm(idle_space=10)
    sm.old_x, sm.to_x = 500, 511
    sm.old_y, sm.to_y = 540, 540
    assert sm._move_start() is True


def test_move_start_true_on_horizontal_left_jump():
    sm = make_sm(idle_space=10)
    sm.old_x, sm.to_x = 500, 489
    sm.old_y, sm.to_y = 540, 540
    assert sm._move_start() is True


def test_move_start_true_on_vertical_jump():
    sm = make_sm(idle_space=10)
    sm.old_x, sm.to_x = 500, 500
    sm.old_y, sm.to_y = 540, 552
    assert sm._move_start() is True


def test_move_start_false_within_idle_space():
    sm = make_sm(idle_space=10)
    sm.old_x, sm.to_x = 500, 505
    sm.old_y, sm.to_y = 540, 543
    assert sm._move_start() is False


# ---------------------------------------------------------------------------
# STOP state transitions (via tick)
# ---------------------------------------------------------------------------


def test_stop_to_awake_when_cursor_jumps_on_first_tick():
    sm = make_sm()
    # Initial to_x/to_y are 0; cursor at 500 is > idle_space away → AWAKE
    sm.tick(Point(500, 540), CENTER, SIZE, BOUNDS)
    assert sm.state == State.AWAKE


def test_stop_to_wash_after_stop_time():
    sm = make_sm(stop_time=2)
    # cursor at (0,0) matches initial to_x/to_y=0 so _move_start stays False
    tick_n(sm, 4, Point(0, 0))
    assert sm.state == State.WASH


def test_stop_to_l_claw_at_left_edge():
    sm = make_sm(stop_time=2)
    left_edge = Point(SIZE.cx // 2, 540)
    tick_n(sm, 4, Point(0, 0), left_edge)
    assert sm.state == State.L_CLAW


def test_stop_to_r_claw_at_right_edge():
    sm = make_sm(stop_time=2)
    right_edge = Point(BOUNDS.right - SIZE.cx // 2, 540)
    tick_n(sm, 4, Point(0, 0), right_edge)
    assert sm.state == State.R_CLAW


def test_stop_to_u_claw_at_top_edge():
    sm = make_sm(stop_time=2)
    top_edge = Point(960, BOUNDS.top + SIZE.cy // 2)
    tick_n(sm, 4, Point(0, 0), top_edge)
    assert sm.state == State.U_CLAW


def test_stop_to_d_claw_at_bottom_edge():
    sm = make_sm(stop_time=2)
    bottom_edge = Point(960, BOUNDS.bottom - SIZE.cy // 2)
    tick_n(sm, 4, Point(0, 0), bottom_edge)
    assert sm.state == State.D_CLAW


# ---------------------------------------------------------------------------
# Idle sequence: STOP → WASH → SCRATCH → YAWN → SLEEP
# ---------------------------------------------------------------------------


def test_full_idle_sequence():
    sm = make_sm(stop_time=2, wash_time=2, scratch_time=2, yawn_time=2)
    cursor = Point(0, 0)

    tick_n(sm, 4, cursor)
    assert sm.state == State.WASH

    tick_n(sm, 4, cursor)
    assert sm.state == State.SCRATCH

    tick_n(sm, 4, cursor)
    assert sm.state == State.YAWN

    tick_n(sm, 4, cursor)
    assert sm.state == State.SLEEP


def test_wash_to_awake_on_cursor_jump():
    sm = make_sm(stop_time=2)
    tick_n(sm, 4, Point(0, 0))
    assert sm.state == State.WASH
    sm.tick(Point(0, 0), CENTER, SIZE, BOUNDS)
    sm.tick(Point(100, 0), CENTER, SIZE, BOUNDS)
    assert sm.state == State.AWAKE


def test_sleep_to_awake_on_cursor_jump():
    sm = make_sm(stop_time=2, wash_time=2, scratch_time=2, yawn_time=2)
    tick_n(sm, 16, Point(0, 0))
    assert sm.state == State.SLEEP
    sm.tick(Point(0, 0), CENTER, SIZE, BOUNDS)
    sm.tick(Point(200, 0), CENTER, SIZE, BOUNDS)
    assert sm.state == State.AWAKE


# ---------------------------------------------------------------------------
# Claw states
# ---------------------------------------------------------------------------


def test_claw_to_scratch_after_claw_time():
    sm = make_sm(stop_time=2, claw_time=2)
    left_edge = Point(SIZE.cx // 2, 540)
    tick_n(sm, 4, Point(0, 0), left_edge)
    assert sm.state == State.L_CLAW
    tick_n(sm, 4, Point(0, 0), left_edge)
    assert sm.state == State.SCRATCH


def test_claw_to_awake_on_cursor_jump():
    sm = make_sm(stop_time=2, claw_time=10)
    left_edge = Point(SIZE.cx // 2, 540)
    tick_n(sm, 4, Point(0, 0), left_edge)
    assert sm.state == State.L_CLAW
    sm.tick(Point(0, 0), left_edge, SIZE, BOUNDS)
    sm.tick(Point(200, 0), left_edge, SIZE, BOUNDS)
    assert sm.state == State.AWAKE


# ---------------------------------------------------------------------------
# AWAKE → correct movement direction (all 8 directions)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dx_offset, dy_offset, expected",
    [
        (200, 0, State.R_MOVE),
        (-200, 0, State.L_MOVE),
        (0, -200, State.U_MOVE),
        (0, 200, State.D_MOVE),
        (100, -100, State.UR_MOVE),
        (-100, -100, State.UL_MOVE),
        (100, 100, State.DR_MOVE),
        (-100, 100, State.DL_MOVE),
    ],
)
def test_awake_picks_correct_direction(dx_offset, dy_offset, expected):
    # awake_time=1, awake_rand=0: needs exactly 3 ticks to reach direction
    # tick1: STOP→AWAKE (cursor far from initial to_x=0)
    # tick2: AWAKE, state_count=0 < 1, waits
    # tick3: AWAKE, state_count=1 >= 1, calls _calc_direction
    sm = make_sm(awake_time=1, awake_rand=0)
    cursor = Point(CENTER.x + dx_offset, CENTER.y + dy_offset)
    tick_n(sm, 3, cursor)
    assert sm.state == expected


# ---------------------------------------------------------------------------
# Movement: position update and boundary clamping
# ---------------------------------------------------------------------------


def test_movement_updates_position_toward_cursor():
    sm = make_sm(awake_time=1, awake_rand=0, max_speed=60)
    cursor_right = Point(1060, 540)
    tick_n(sm, 3, cursor_right)
    assert sm.state == State.R_MOVE
    result = sm.tick(cursor_right, CENTER, SIZE, BOUNDS)
    assert result.x > CENTER.x


def test_movement_clamps_x_at_right_boundary():
    sm = make_sm(awake_time=1, awake_rand=0, max_speed=100)
    tick_n(sm, 3, Point(1100, 540))
    near_right = Point(1900, 540)
    result = sm.tick(Point(2000, 540), near_right, SIZE, BOUNDS)
    assert result.x <= BOUNDS.right - SIZE.cx // 2


def test_movement_stops_when_pet_reaches_cursor():
    sm = make_sm(awake_time=1, awake_rand=0, max_speed=60)
    tick_n(sm, 3, Point(1060, 540))
    assert sm.state == State.R_MOVE
    # cursor at exact same position as pet → dx=dy=0 → _calc_direction → STOP
    sm.tick(CENTER, CENTER, SIZE, BOUNDS)
    assert sm.state == State.STOP


# ---------------------------------------------------------------------------
# Frame index cycling
# ---------------------------------------------------------------------------


def test_frame_index_on_transition_tick_is_first_frame():
    sm = make_sm(awake_time=1, awake_rand=0)
    # tick 3 is the AWAKE→R_MOVE transition; _set_new_state resets tick_count=0
    r = tick_n(sm, 3, Point(1100, 540))
    assert r.frame_index == 5  # animation[R_MOVE][0]


def test_frame_index_alternates_in_move_state():
    sm = make_sm(awake_time=1, awake_rand=0)
    tick_n(sm, 3, Point(1100, 540))  # → R_MOVE, tick_count=0
    r4 = sm.tick(Point(1100, 540), CENTER, SIZE, BOUNDS)
    r5 = sm.tick(Point(1100, 540), CENTER, SIZE, BOUNDS)
    assert r4.frame_index == 6  # animation[R_MOVE][1]
    assert r5.frame_index == 5  # animation[R_MOVE][2], cycles back


def test_frame_index_for_stop_state_is_constant():
    sm = make_sm()
    # cursor at (0,0) stays in STOP (no cursor jump from initial to_x=0)
    result = sm.tick(Point(0, 0), CENTER, SIZE, BOUNDS)
    assert result.frame_index == 28  # animation[STOP] = [28, 28, 28, 28]


# ---------------------------------------------------------------------------
# Idle wandering
# ---------------------------------------------------------------------------

IDLE_CURSOR = Point(0, 0)


def make_sleeping_sm(**overrides):
    sm = make_sm(
        stop_time=2,
        wash_time=2,
        scratch_time=2,
        yawn_time=2,
        awake_time=1,
        **overrides,
    )
    tick_n(sm, 16, IDLE_CURSOR)
    assert sm.state == State.SLEEP
    return sm


def test_wander_triggers_after_sleeping_long_enough():
    sm = make_sleeping_sm(wander_enabled=True, wander_time=2, wander_rand=0)
    # state_count increments every 2 ticks; below threshold → still asleep
    tick_n(sm, 3, IDLE_CURSOR)
    assert sm.state == State.SLEEP
    tick_n(sm, 1, IDLE_CURSOR)
    assert sm.state == State.AWAKE
    assert sm.wander_target is not None


def test_wander_disabled_sleeps_forever():
    sm = make_sleeping_sm(wander_enabled=False, wander_time=2, wander_rand=0)
    tick_n(sm, 50, IDLE_CURSOR)
    assert sm.state == State.SLEEP
    assert sm.wander_target is None


def test_wander_target_is_within_bounds():
    sm = make_sleeping_sm(wander_enabled=True, wander_time=2, wander_rand=0)
    tick_n(sm, 4, IDLE_CURSOR)
    target = sm.wander_target
    assert BOUNDS.left + SIZE.cx // 2 <= target.x
    assert target.x <= BOUNDS.right - SIZE.cx // 2
    assert BOUNDS.top + SIZE.cy // 2 <= target.y
    assert target.y <= BOUNDS.bottom - SIZE.cy // 2


def test_wander_moves_toward_target(monkeypatch):
    monkeypatch.setattr(
        NekoStateMachine,
        "_pick_wander_target",
        lambda self, size, bounds: Point(1500, 540),
    )
    sm = make_sleeping_sm(wander_enabled=True, wander_time=2, wander_rand=0)
    tick_n(sm, 4, IDLE_CURSOR)  # SLEEP → AWAKE with wander target
    assert sm.wander_target == Point(1500, 540)
    # AWAKE waits awake_time, then picks a direction toward the target
    result = tick_n(sm, 3, IDLE_CURSOR)
    assert sm.state == State.R_MOVE
    assert result.x > CENTER.x


def test_cursor_movement_cancels_wander(monkeypatch):
    monkeypatch.setattr(
        NekoStateMachine,
        "_pick_wander_target",
        lambda self, size, bounds: Point(1500, 540),
    )
    sm = make_sleeping_sm(wander_enabled=True, wander_time=2, wander_rand=0)
    tick_n(sm, 7, IDLE_CURSOR)  # wandering: R_MOVE toward (1500, 540)
    assert sm.state == State.R_MOVE
    sm.tick(Point(300, 540), CENTER, SIZE, BOUNDS)
    assert sm.wander_target is None
    # next direction calc chases the real cursor (left of center)
    sm.tick(Point(300, 540), CENTER, SIZE, BOUNDS)
    assert sm.state == State.L_MOVE


def test_reaching_stop_clears_wander_target():
    sm = make_sm(wander_enabled=True, wander_time=2, wander_rand=0)
    sm.wander_target = Point(1500, 540)
    sm.state = State.R_MOVE
    sm._set_new_state(State.STOP)
    assert sm.wander_target is None
