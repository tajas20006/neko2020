import math
import random
from dataclasses import dataclass
from enum import Enum, auto

from neko2020.domain.settings import BehaviorSettings
from neko2020.domain.value_objects import Point, Rect, Size

# sector borders when the circle is divided into 8 directions
SIN_PI_8 = math.sin(math.pi / 8)
SIN_3PI_8 = math.sin(math.pi * 3 / 8)


class State(Enum):
    STOP = auto()
    WASH = auto()
    SCRATCH = auto()
    YAWN = auto()
    SLEEP = auto()
    AWAKE = auto()
    U_MOVE = auto()
    D_MOVE = auto()
    L_MOVE = auto()
    R_MOVE = auto()
    UL_MOVE = auto()
    UR_MOVE = auto()
    DL_MOVE = auto()
    DR_MOVE = auto()
    U_CLAW = auto()
    D_CLAW = auto()
    L_CLAW = auto()
    R_CLAW = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


_MOVE_STATES = frozenset(
    {
        State.U_MOVE,
        State.D_MOVE,
        State.L_MOVE,
        State.R_MOVE,
        State.UL_MOVE,
        State.UR_MOVE,
        State.DL_MOVE,
        State.DR_MOVE,
    }
)


@dataclass(frozen=True, slots=True)
class TickResult:
    state: State
    # position in the state's 4-step animation cycle (0-3)
    phase: int
    x: int
    y: int


class NekoStateMachine:
    def __init__(self, settings: BehaviorSettings):
        self.settings = settings

        self.dx = 0
        self.dy = 0
        self.to_x = 0
        self.to_y = 0
        self.old_x = 0
        self.old_y = 0
        self.tick_count = 0
        self.state_count = 0
        self.sub_tick = 0
        self.state = State.STOP
        self.wander_target: Point | None = None

    def _move_start(self):
        return (
            self.old_x < self.to_x - self.settings.idle_space
            or self.old_x > self.to_x + self.settings.idle_space
            or self.old_y < self.to_y - self.settings.idle_space
            or self.old_y > self.to_y + self.settings.idle_space
        )

    def _calc_direction(self):
        if self.dx == 0 and self.dy == 0:
            return self._set_new_state(State.STOP)

        sin_theta = -self.dy / math.hypot(self.dx, self.dy)
        # straight up/down are shared by both halves of the circle
        if sin_theta > SIN_3PI_8:
            state = State.U_MOVE
        elif sin_theta > SIN_PI_8:
            state = State.UR_MOVE if self.dx > 0 else State.UL_MOVE
        elif sin_theta > -SIN_PI_8:
            state = State.R_MOVE if self.dx > 0 else State.L_MOVE
        elif sin_theta > -SIN_3PI_8:
            state = State.DR_MOVE if self.dx > 0 else State.DL_MOVE
        else:
            state = State.D_MOVE
        return self._set_new_state(state)

    def _set_new_state(self, state):
        if self.state == state:
            return
        if state == State.STOP:
            # arrived (or gave up): resume the normal idle cycle
            self.wander_target = None
        self.tick_count = 0
        self.state_count = 0
        self.sub_tick = 0
        self.state = state
        return self.state

    def _pick_wander_target(self, size: Size, bounds: Rect) -> Point:
        half_cx = size.cx // 2
        half_cy = size.cy // 2
        return Point(
            random.randint(bounds.left + half_cx, bounds.right - half_cx),
            random.randint(bounds.top + half_cy, bounds.bottom - half_cy),
        )

    def tick(
        self,
        cursor: Point,
        position: Point,
        size: Size,
        bounds: Rect,
    ) -> TickResult:
        self.old_x = self.to_x
        self.old_y = self.to_y
        self.to_x = cursor.x
        self.to_y = cursor.y

        # real cursor movement always cancels wandering
        if self.wander_target is not None and self._move_start():
            self.wander_target = None

        if self.wander_target is not None:
            target_x = self.wander_target.x
            target_y = self.wander_target.y
        else:
            target_x = cursor.x
            target_y = cursor.y

        half_cx = size.cx // 2
        half_cy = size.cy // 2
        if target_x <= bounds.left + half_cx:
            dx = bounds.left + half_cx - position.x
        elif target_x >= bounds.right - half_cx:
            dx = bounds.right - half_cx - position.x
        else:
            dx = target_x - position.x + self.settings.offset.x
        if target_y <= bounds.top + half_cy:
            dy = bounds.top + half_cy - position.y
        elif target_y >= bounds.bottom - half_cy:
            dy = bounds.bottom - half_cy - position.y
        else:
            dy = target_y - position.y + self.settings.offset.y
        double_length = dx * dx + dy * dy

        if double_length != 0:
            length = math.sqrt(double_length)
            if length <= self.settings.max_speed:
                self.dx = dx
                self.dy = dy
            else:
                self.dx = int(self.settings.max_speed * dx / length)
                self.dy = int(self.settings.max_speed * dy / length)
        else:
            self.dx = 0
            self.dy = 0

        # The image only advances once every `frame_hold` ticks, so a high
        # fps does not make the sprite swap faster.
        self.sub_tick += 1
        if self.sub_tick >= max(1, self.settings.frame_hold):
            self.sub_tick = 0
            self.tick_count = (self.tick_count + 1) % 4
            if self.tick_count % 2 == 0:
                self.state_count += 1

        result_x = position.x
        result_y = position.y

        if self.state == State.STOP:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.settings.stop_time:
                half_cx = size.cx // 2
                half_cy = size.cy // 2
                if position.x <= bounds.left + half_cx:
                    self._set_new_state(State.L_CLAW)
                elif position.x >= bounds.right - half_cx:
                    self._set_new_state(State.R_CLAW)
                elif position.y <= bounds.top + half_cy:
                    self._set_new_state(State.U_CLAW)
                elif position.y >= bounds.bottom - half_cy:
                    self._set_new_state(State.D_CLAW)
                else:
                    self._set_new_state(State.WASH)
        elif self.state == State.WASH:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.settings.wash_time:
                self._set_new_state(State.SCRATCH)
        elif self.state == State.SCRATCH:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.settings.scratch_time:
                self._set_new_state(State.YAWN)
        elif self.state == State.YAWN:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.settings.yawn_time:
                self._set_new_state(State.SLEEP)
        elif self.state == State.SLEEP:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.settings.wander_enabled and self.state_count >= (
                self.settings.wander_time
                + int(random.random() * self.settings.wander_rand)
            ):
                self.wander_target = self._pick_wander_target(size, bounds)
                self._set_new_state(State.AWAKE)
        elif self.state == State.AWAKE:
            if self.state_count >= self.settings.awake_time + int(
                random.random() * self.settings.awake_rand
            ):
                self._calc_direction()
        elif self.state in _MOVE_STATES:
            x = position.x
            y = position.y
            new_x = x + self.dx
            new_y = y + self.dy
            x_min = bounds.left + size.cx // 2
            x_max = bounds.right - size.cx // 2
            y_min = bounds.top + size.cy // 2
            y_max = bounds.bottom - size.cy // 2
            outside = (
                new_x <= x_min
                or new_x >= x_max
                or new_y <= y_min
                or new_y >= y_max
            )

            self._calc_direction()

            if new_x < x_min:
                new_x = x_min
            elif new_x > x_max:
                new_x = x_max
            if new_y < y_min:
                new_y = y_min
            elif new_y > y_max:
                new_y = y_max
            not_moved = new_x == x and new_y == y

            if outside and not_moved:
                self._set_new_state(State.STOP)
            else:
                result_x = new_x
                result_y = new_y
        elif self.state in {
            State.U_CLAW,
            State.D_CLAW,
            State.L_CLAW,
            State.R_CLAW,
        }:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.settings.claw_time:
                self._set_new_state(State.SCRATCH)
        else:
            self._set_new_state(State.STOP)

        return TickResult(
            state=self.state,
            phase=self.tick_count,
            x=result_x,
            y=result_y,
        )
