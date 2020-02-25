from abc import ABC, abstractmethod
from typing import Tuple
import logging

from OpenGL import GL

from .window import Window
from .camera import Camera
from . import color


class Viewport:
    @abstractmethod
    def __init__(self,
                 window: Window,
                 x: int = 0,
                 y: int = 0,
                 background_col: color.Color = color.BLACK) -> None:
        self.window = window
        self.screens = []
        self.push_screen(x, y, window.width, window.height)
        self.background_col = background_col

    @abstractmethod
    def on_resize(self, width: int, height: int) -> None:
        raise NotImplementedError()

    def set_screen(self, x: int, y: int, w: int, h: int) -> None:
        self.screens[0] = (x, y, w, h)
        GL.glViewport(x, y, w, h)

    def push_screen(self, x: int, y: int, w: int, h: int) -> None:
        screen = (x, y, w, h)
        GL.glViewport(*screen)
        self.screens.append(screen)

    def pop_screen(self) -> None:
        if len(self.screens) == 1:
            logging.warning("Unable to pop last viewport screen")
        self.screens.pop()
        self.set_screen(*self.screens[-1])

    def get_screen(self) -> Tuple[int, int, int, int]:
        return self.x, self.y, self.window.width, self.window.height

    def clear_viewport(self) -> None:
        self.window.clear(self.background_col)


class ConstantViewport(Viewport):
    def __init__(self,
                 window: Window,
                 constant_width: int,
                 constant_height: int,
                 x: int = 0,
                 y: int = 0) -> None:
        super().__init__(window, x, y)
        self.constant_width = constant_width
        self.constant_height = constant_height

    def on_resize(self, width: int, height: int) -> None:
        target_aspect = self.constant_width / self.constant_height

        w = width
        h = int(w / target_aspect + 0.5)
        if h > height:
            h = height
            w = int(h * target_aspect + 0.5)

        x_pos = (width / 2) - (w / 2)
        y_pos = (height / 2) - (h / 2)

        self.set_screen(int(x_pos), int(y_pos), w, h)
