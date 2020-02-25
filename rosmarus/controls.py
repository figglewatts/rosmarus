from dataclasses import dataclass
from enum import Enum
from itertools import repeat
from typing import Mapping, List

import glfw
import glm


class InputState(Enum):
    UP = glfw.RELEASE
    DOWN = glfw.PRESS
    HELD = glfw.REPEAT
    IDLE = 3


@dataclass
class Input:
    code: int
    state_index: int


NUM_KEYS = 348
NUM_MOUSE_BUTTONS = 8

inputs: Mapping[str, Input] = {}
states: List[InputState] = []
keys: List[bool] = [False] * (NUM_KEYS + NUM_MOUSE_BUTTONS)

mouse_pos: glm.vec2 = glm.vec2()
scroll_state: glm.vec2 = glm.vec2()


def _handle_input(state: InputState, button: bool) -> InputState:
    # state machine for input events
    if button:
        if state == InputState.DOWN:
            return InputState.HELD
        elif state != InputState.HELD:
            return InputState.DOWN
    else:
        if state != InputState.UP and (state == InputState.DOWN
                                       or state == InputState.HELD):
            return InputState.UP
        else:
            return InputState.IDLE
    return state


def add(name: str, code: int) -> None:
    inputs[name] = Input(code, len(states))
    states.append(InputState.IDLE)


def add_mouse(name: str, code: int) -> None:
    inputs[name] = Input(code + NUM_KEYS, len(states))
    states.append(InputState.IDLE)


def check(name: str, state: InputState) -> bool:
    return states[inputs[name].state_index] == state


def handle() -> None:
    """Call me every update timestep before anything happens."""
    for btn in inputs.values():
        last_state = states[btn.state_index]
        key_status = keys[btn.code]
        new_state = _handle_input(last_state, key_status)
        states[btn.state_index] = new_state


def key_callback(window, key, scancode, action, mode) -> None:
    keys[key] = action


def cursor_pos_callback(window, x, y) -> None:
    mouse_pos.x = x
    mouse_pos.y = y


def mouse_button_callback(window, button, action, mods) -> None:
    keys[NUM_KEYS + button] = action


def scroll_callback(window, x_offset, y_offset) -> None:
    scroll_state += glm.vec2(x_offset, y_offset)