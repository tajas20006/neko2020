import pytest

from neko2020.adapters.sprite_map import sprite_name
from neko2020.domain.state_machine import State
from neko2020.infrastructure.image_loader import ICON_NAMES

# The frame indices the state machine used to hard-code, kept here to
# pin the (state, phase) -> sprite mapping against ICON_NAMES order.
_LEGACY_INDICES = {
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


@pytest.mark.parametrize("state", list(State))
def test_every_state_maps_to_known_sprites(state):
    for phase in range(4):
        assert sprite_name(state, phase) in ICON_NAMES


@pytest.mark.parametrize("state", list(State))
def test_mapping_matches_legacy_indices(state):
    names = [sprite_name(state, phase) for phase in range(4)]
    assert names == [ICON_NAMES[i] for i in _LEGACY_INDICES[state]]


def test_every_icon_name_is_used():
    used = {sprite_name(s, p) for s in State for p in range(4)}
    assert used == set(ICON_NAMES)
