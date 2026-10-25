"""Which sprite file each (state, animation phase) is drawn with.

The names must match the files of a sprite set (see
``infrastructure.image_loader.ICON_NAMES``).
"""

from neko2020.domain.state_machine import State


def _alternate(a: str, b: str) -> tuple[str, str, str, str]:
    return (a, b, a, b)


_SPRITES: dict[State, tuple[str, str, str, str]] = {
    State.STOP: ("yawn2",) * 4,
    State.WASH: _alternate("wash2", "yawn2"),
    State.SCRATCH: _alternate("scratch1", "scratch2"),
    State.YAWN: _alternate("yawn2", "yawn3"),
    State.SLEEP: ("sleep1", "sleep1", "sleep2", "sleep2"),
    State.AWAKE: ("Awake",) * 4,
    State.U_MOVE: _alternate("up1", "up2"),
    State.D_MOVE: _alternate("down1", "down2"),
    State.L_MOVE: _alternate("left1", "left2"),
    State.R_MOVE: _alternate("right1", "right2"),
    State.UL_MOVE: _alternate("upleft1", "upleft2"),
    State.UR_MOVE: _alternate("upright1", "upright2"),
    State.DL_MOVE: _alternate("downleft1", "downleft2"),
    State.DR_MOVE: _alternate("downright1", "downright2"),
    State.U_CLAW: _alternate("upclaw1", "upclaw2"),
    State.D_CLAW: _alternate("downclaw1", "downclaw2"),
    State.L_CLAW: _alternate("leftclaw1", "leftclaw2"),
    State.R_CLAW: _alternate("rightclaw1", "rightclaw2"),
}


def sprite_name(state: State, phase: int) -> str:
    return _SPRITES[state][phase]
