import math
import random
from enum import Enum, auto
from neko2020.utils import configs, classes
from neko2020 import pet

# animation control constants
STOP_TIME = 4
WASH_TIME = 10
SCRATCH_TIME = 4
YAWN_TIME = 3
AWAKE_TIME = 3
CLAW_TIME = 10

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


class Neko:
    def __init__(self, root, canvas):
        self.root = root
        self.pet = pet.Pet(canvas)

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
        self.offset = classes.Point(
            configs.get_int("offset.x"), configs.get_int("offset.y")
        )
        self.min_speed = configs.get_int("speed.min")
        self.max_speed = configs.get_int("speed.max")
        # self.offset = classes.Point(0, -50)
        # self.min_speed = 2
        # self.max_speed = 48

        self.idle_space = configs.get_int("idle_space")
        # self.idle_space = 6
        self.action_count = 0
        self.tick_count = 0
        self.state_count = 0
        self.state = State.STOP

    def move_start(self):
        return (
            self.old_x < self.to_x - self.idle_space
            or self.old_x > self.to_x + self.idle_space
            or self.old_y < self.to_y - self.idle_space
            or self.old_y > self.to_y + self.idle_space
        )

    def calc_direction(self):
        if self.dx == 0 and self.dy == 0:
            return self.set_new_state(State.STOP)

        length = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        sin_theta = -self.dy / length

        if self.dx > 0:
            if sin_theta > SinPiPer8Times3:
                return self.set_new_state(State.U_MOVE)
            if sin_theta <= SinPiPer8Times3 and sin_theta > SinPiPer8:
                return self.set_new_state(State.UR_MOVE)
            if sin_theta <= SinPiPer8 and sin_theta > -SinPiPer8:
                return self.set_new_state(State.R_MOVE)
            if sin_theta <= -SinPiPer8 and sin_theta > -SinPiPer8Times3:
                return self.set_new_state(State.DR_MOVE)
            if self.state != State.D_MOVE:
                return self.set_new_state(State.D_MOVE)

        # moving left
        if sin_theta > SinPiPer8Times3:
            return self.set_new_state(State.U_MOVE)
        if sin_theta <= SinPiPer8Times3 and sin_theta > SinPiPer8:
            return self.set_new_state(State.UL_MOVE)
        if sin_theta <= SinPiPer8 and sin_theta > -SinPiPer8:
            return self.set_new_state(State.L_MOVE)
        if sin_theta <= -SinPiPer8 and sin_theta > -SinPiPer8Times3:
            return self.set_new_state(State.DL_MOVE)
        if self.state != State.D_MOVE:
            return self.set_new_state(State.D_MOVE)

    def run_towards(self, new_x, new_y):
        self.old_x = self.to_x
        self.old_y = self.to_y
        self.to_x = new_x
        self.to_y = new_y

        dx = (
            self.to_x
            - self.pet.get_position().x
            - self.pet.get_size().cx / 2  # stop in middle of cursor
            + self.offset.x  # custom offset
        )
        if self.to_y == self.pet.get_bounds_rect().bottom - 1:
            # if cursor is at the very bottom, ignore offset
            dy = self.to_y - self.pet.get_position().y - self.pet.get_size().cy
        else:
            dy = (
                self.to_y
                - self.pet.get_position().y
                - self.pet.get_size().cy
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

        if self.state == State.STOP:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            elif self.state_count >= STOP_TIME:
                if self.dx < 0 and self.pet.get_position().x <= 0:
                    self.set_new_state(State.L_CLAW)
                elif (
                    self.dx > 0
                    and self.pet.get_position().x
                    >= (
                        self.pet.get_bounds_rect().right
                        - self.pet.get_bounds_rect().left
                    )
                    - self.pet.get_size().cx
                ):
                    self.set_new_state(State.R_CLAW)
                elif self.dy < 0 and self.pet.get_position().y <= 0:
                    self.set_new_state(State.U_CLAW)
                elif self.dy >= 0 and self.pet.get_position().y >= (
                    self.pet.get_bounds_rect().bottom
                    - self.pet.get_bounds_rect().top
                ) - self.pet.get_size().cy + configs.get_int("offset.y"):
                    self.set_new_state(State.D_CLAW)
                else:
                    self.set_new_state(State.WASH)
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state == State.WASH:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            elif self.state_count >= WASH_TIME:
                self.set_new_state(State.SCRATCH)
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state == State.SCRATCH:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            elif self.state_count >= SCRATCH_TIME:
                self.set_new_state(State.YAWN)
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state == State.YAWN:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            elif self.state_count >= YAWN_TIME:
                self.set_new_state(State.SLEEP)
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state == State.SLEEP:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state == State.AWAKE:
            if self.state_count >= AWAKE_TIME + int(random.random() * 20):
                self.calc_direction()
            self.pet.set_image(self.get_state_animation_frame_index())
        elif self.state in {
            # fmt: off
            State.U_MOVE, State.D_MOVE, State.L_MOVE, State.R_MOVE,
            State.UL_MOVE, State.UR_MOVE, State.DL_MOVE, State.DR_MOVE,
            # fmt: on
        }:
            x = self.pet.get_position().x
            y = self.pet.get_position().y
            new_x = x + self.dx
            new_y = y + self.dy
            width = (
                self.pet.get_bounds_rect().right
                - self.pet.get_bounds_rect().left
                - self.pet.get_size().cx
            )
            height = (
                self.pet.get_bounds_rect().bottom
                - self.pet.get_bounds_rect().top
                - self.pet.get_size().cy
            )
            outside = (
                new_x <= 0 or new_x >= width or new_y <= 0 or new_y >= height
            )

            self.calc_direction()

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
                self.set_new_state(State.STOP)
            else:
                self.pet.set_image_and_move_to(
                    self.get_state_animation_frame_index(), new_x, new_y
                )
        elif self.state in {
            # fmt: off
            State.U_CLAW, State.D_CLAW, State.L_CLAW, State.R_CLAW,
            # fmt: on
        }:
            if self.move_start():
                self.set_new_state(State.AWAKE)
            elif self.state_count >= CLAW_TIME:
                self.set_new_state(State.SCRATCH)
            self.pet.set_image(self.get_state_animation_frame_index())
        else:
            self.set_new_state(State.STOP)
            self.pet.set_image(self.get_state_animation_frame_index())

    def get_state_animation_frame_index(self):
        return self.animation[self.state][self.tick_count]

    def set_new_state(self, state):
        if self.state == state:
            return
        self.tick_count = 0
        self.state_count = 0
        self.state = state
        return self.state

    def update(self):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.run_towards(x, y)
