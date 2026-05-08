import math
import random
from dataclasses import dataclass
from enum import Enum, auto

from neko2020.domain.value_objects import Point, Rect, Size

# define angle border
# sin(pi / 8)
SinPiPer8 = 0.3826834323651
# sin(pi/8*3)
SinPiPer8Times3 = 0.9238795325113


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


@dataclass(frozen=True)
class TickResult:
    frame_index: int
    x: int
    y: int


class NekoStateMachine:
    def __init__(
        self,
        *,
        stop_time: int,
        wash_time: int,
        scratch_time: int,
        yawn_time: int,
        awake_time: int,
        claw_time: int,
        awake_rand: int,
        min_speed: int,
        max_speed: int,
        idle_space: int,
        offset: Point,
    ):
        self.STOP_TIME = stop_time
        self.WASH_TIME = wash_time
        self.SCRATCH_TIME = scratch_time
        self.YAWN_TIME = yawn_time
        self.AWAKE_TIME = awake_time
        self.CLAW_TIME = claw_time
        self.AWK_RND = awake_rand

        self.animation = {
            State.STOP: [28, 28, 28, 28],
            State.WASH: [25, 28, 25, 28],
            State.SCRATCH: [26, 27, 26, 27],
            State.YAWN: [28, 29, 28, 29],
            State.SLEEP: [30, 30, 31, 31],
            State.AWAKE: [0, 0, 0, 0],
            State.U_MOVE: [1, 2, 1, 2],
            State.D_MOVE: [9, 10, 9, 10],
            State.L_MOVE: [13, 14, 13, 14],
            State.R_MOVE: [5, 6, 5, 6],
            State.UL_MOVE: [15, 16, 15, 16],
            State.UR_MOVE: [3, 4, 3, 4],
            State.DL_MOVE: [11, 12, 11, 12],
            State.DR_MOVE: [7, 8, 7, 8],
            State.U_CLAW: [17, 18, 17, 18],
            State.D_CLAW: [23, 24, 23, 24],
            State.L_CLAW: [21, 22, 21, 22],
            State.R_CLAW: [19, 20, 19, 20],
        }

        self.dx = 0
        self.dy = 0
        self.to_x = 0
        self.to_y = 0
        self.old_x = 0
        self.old_y = 0
        self.offset = offset
        self.min_speed = min_speed
        self.max_speed = max_speed

        self.idle_space = idle_space
        self.action_count = 0
        self.tick_count = 0
        self.state_count = 0
        self.state = State.STOP

    def _move_start(self):
        return (
            self.old_x < self.to_x - self.idle_space
            or self.old_x > self.to_x + self.idle_space
            or self.old_y < self.to_y - self.idle_space
            or self.old_y > self.to_y + self.idle_space
        )

    def _calc_direction(self):
        if self.dx == 0 and self.dy == 0:
            return self._set_new_state(State.STOP)

        length = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        sin_theta = -self.dy / length

        if self.dx > 0:
            if sin_theta > SinPiPer8Times3:
                return self._set_new_state(State.U_MOVE)
            if sin_theta <= SinPiPer8Times3 and sin_theta > SinPiPer8:
                return self._set_new_state(State.UR_MOVE)
            if sin_theta <= SinPiPer8 and sin_theta > -SinPiPer8:
                return self._set_new_state(State.R_MOVE)
            if sin_theta <= -SinPiPer8 and sin_theta > -SinPiPer8Times3:
                return self._set_new_state(State.DR_MOVE)
            if self.state != State.D_MOVE:
                return self._set_new_state(State.D_MOVE)

        # moving left
        if sin_theta > SinPiPer8Times3:
            return self._set_new_state(State.U_MOVE)
        if sin_theta <= SinPiPer8Times3 and sin_theta > SinPiPer8:
            return self._set_new_state(State.UL_MOVE)
        if sin_theta <= SinPiPer8 and sin_theta > -SinPiPer8:
            return self._set_new_state(State.L_MOVE)
        if sin_theta <= -SinPiPer8 and sin_theta > -SinPiPer8Times3:
            return self._set_new_state(State.DL_MOVE)
        if self.state != State.D_MOVE:
            return self._set_new_state(State.D_MOVE)

    def _set_new_state(self, state):
        if self.state == state:
            return
        self.tick_count = 0
        self.state_count = 0
        self.state = state
        return self.state

    def _frame_index(self):
        return self.animation[self.state][self.tick_count]

    def tick(
        self,
        cursor: Point,
        position: Point,
        size: Size,
        bounds: Rect,
    ) -> TickResult:
        new_x_target = cursor.x
        new_y_target = cursor.y

        self.old_x = self.to_x
        self.old_y = self.to_y
        self.to_x = new_x_target
        self.to_y = new_y_target

        dx = (
            self.to_x
            - position.x
            - size.cx / 2  # stop in middle of cursor
            + self.offset.x  # custom offset
        )
        if self.to_y == bounds.bottom - 1:
            # if cursor is at the very bottom, ignore offset
            dy = self.to_y - position.y - size.cy
        else:
            dy = (
                self.to_y
                - position.y
                - size.cy
                + 1  # stop just above the cursor
                + self.offset.y  # custom offset
            )
        double_length = dx * dx + dy * dy

        if double_length != 0:
            length = math.sqrt(double_length)
            if length <= self.max_speed:
                self.dx = dx
                self.dy = dy
            else:
                self.dx = int(self.max_speed * dx / length)
                self.dy = int(self.max_speed * dy / length)
        else:
            self.dx = 0
            self.dy = 0

        self.tick_count = (self.tick_count + 1) % 4
        if self.tick_count % 2 == 0:
            self.state_count += 1

        result_x = position.x
        result_y = position.y

        if self.state == State.STOP:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.STOP_TIME:
                if self.dx < 0 and position.x <= 0:
                    self._set_new_state(State.L_CLAW)
                elif (
                    self.dx > 0
                    and position.x >= (bounds.right - bounds.left) - size.cx
                ):
                    self._set_new_state(State.R_CLAW)
                elif self.dy < 0 and position.y <= 0:
                    self._set_new_state(State.U_CLAW)
                elif (
                    self.dy >= 0
                    and position.y
                    >= (bounds.bottom - bounds.top) - size.cy + self.offset.y
                ):
                    self._set_new_state(State.D_CLAW)
                else:
                    self._set_new_state(State.WASH)
        elif self.state == State.WASH:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.WASH_TIME:
                self._set_new_state(State.SCRATCH)
        elif self.state == State.SCRATCH:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.SCRATCH_TIME:
                self._set_new_state(State.YAWN)
        elif self.state == State.YAWN:
            if self._move_start():
                self._set_new_state(State.AWAKE)
            elif self.state_count >= self.YAWN_TIME:
                self._set_new_state(State.SLEEP)
        elif self.state == State.SLEEP:
            if self._move_start():
                self._set_new_state(State.AWAKE)
        elif self.state == State.AWAKE:
            if self.state_count >= self.AWAKE_TIME + int(
                random.random() * self.AWK_RND
            ):
                self._calc_direction()
        elif self.state in {
            State.U_MOVE,
            State.D_MOVE,
            State.L_MOVE,
            State.R_MOVE,
            State.UL_MOVE,
            State.UR_MOVE,
            State.DL_MOVE,
            State.DR_MOVE,
        }:
            x = position.x
            y = position.y
            new_x = x + self.dx
            new_y = y + self.dy
            width = (bounds.right - bounds.left) - size.cx
            height = (bounds.bottom - bounds.top) - size.cy
            outside = (
                new_x <= 0 or new_x >= width or new_y <= 0 or new_y >= height
            )

            self._calc_direction()

            if new_x < 0:
                new_x = 0
            elif new_x > width:
                new_x = width
            if new_y < 0:
                new_y = 0
            elif new_y > height:
                new_y = height
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
            elif self.state_count >= self.CLAW_TIME:
                self._set_new_state(State.SCRATCH)
        else:
            self._set_new_state(State.STOP)

        return TickResult(
            frame_index=self._frame_index(),
            x=result_x,
            y=result_y,
        )
