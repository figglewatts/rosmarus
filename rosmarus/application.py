from contextlib import contextmanager
from typing import Tuple, ContextManager, Callable

import glfw

from .graphics.window import Window
from .graphics.gl_context import GLContext
from .util import make_path_safe
from . import resources


class Application:
    def __init__(self,
                 name: str,
                 data_path: str = None,
                 update_frequency_hz: float = 60,
                 on_start: Callable[..., None] = None,
                 on_exit: Callable[..., None] = None,
                 on_update: Callable[[float], None] = None,
                 on_render: Callable[..., None] = None) -> None:
        self.name = name
        if data_path is None:
            data_path = make_path_safe(f"{name}_data")
        self.data_path = data_path
        self.on_start = on_start
        self.on_exit = on_exit
        self.on_update = on_update
        self.on_render = on_render
        self.target_delta_time = 1.0 / update_frequency_hz
        self.elapsed_time = 0
        resources._register_data_path(data_path)

    def set_start_callback(self, callback: Callable[..., None]) -> None:
        self.on_start = callback

    def set_exit_callback(self, callback: Callable[..., None]) -> None:
        self.on_exit = callback

    def set_update_callback(self, callback: Callable[[float], None]) -> None:
        self.on_update = callback

    def set_render_callback(self, callback: Callable[..., None]) -> None:
        self.on_render = callback

    def _run_callback(self, callback: Callable[..., None], *args,
                      **kwargs) -> None:
        if callback is not None:
            callback(*args, **kwargs)

    def main_loop(self, window: Window) -> None:
        current_time = glfw.get_time()
        accumulator = 0
        while not glfw.window_should_close(window.glfw_window):
            new_time = glfw.get_time()
            frame_time = new_time - current_time
            current_time = new_time
            accumulator += frame_time

            # update as fast as possible, but only render at a set delta time
            while accumulator >= self.target_delta_time:
                self._run_callback(self.on_update, frame_time)
                accumulator -= self.target_delta_time
                self.elapsed_time += self.target_delta_time

            self._run_callback(self.on_render)

            glfw.swap_buffers(window.glfw_window)
            glfw.poll_events()

    @contextmanager
    def make_window(self, width: int, height: int,
                    gl_version: Tuple[int, int]) -> ContextManager[Window]:
        major, minor = gl_version
        window = Window(self.name, width, height, GLContext(major, minor))
        try:
            initialized = window._initialize()
            self._run_callback(self.on_start)
            yield initialized
        finally:
            self._run_callback(self.on_exit)
            window._cleanup()