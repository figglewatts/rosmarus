from contextlib import contextmanager
from typing import Tuple, ContextManager, Callable

from .graphics.window import Window
from .graphics.gl_context import GLContext
from .util import make_path_safe
from . import resources


class Application:
    def __init__(self,
                 name: str,
                 data_path: str = None,
                 on_start: Callable[..., None] = None,
                 on_exit: Callable[..., None] = None) -> None:
        self.name = name
        if data_path is None:
            data_path = make_path_safe(f"{name}_data")
        self.data_path = data_path
        self.on_start = on_start
        self.on_exit = on_exit
        resources._register_data_path(data_path)

    def set_start_callback(self, callback: Callable[..., None]) -> None:
        self.on_start = callback

    def set_exit_callback(self, callback: Callable[..., None]) -> None:
        self.on_exit = callback

    def _run_callback(self, callback: Callable[..., None], *args,
                      **kwargs) -> None:
        if callback is not None:
            callback(args, kwargs)

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