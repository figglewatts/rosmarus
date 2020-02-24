from __future__ import annotations
from typing import Callable

import glfw
from OpenGL import GL

from .gl_context import GLContext
from . import color
from ..math.rect import Rect


class Window:
    viewport = Rect()

    def __init__(self,
                 title: str,
                 width: int,
                 height: int,
                 gl_context: GLContext,
                 on_resize: Callable[..., None] = None) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.gl_context = gl_context
        self.on_resize = on_resize
        self.initialized = False
        Window.viewport = Rect(0, 0, width, height)

    def __enter__(self) -> Window:
        return self._initialize()

    def __exit__(self, type, value, traceback) -> None:
        self._cleanup()

    def _initialize(self) -> Window:
        if not glfw.init():
            raise RuntimeError("Unable to initialize GLFW")

        self.glfw_window = glfw.create_window(self.width, self.height,
                                              self.title, None, None)
        if not self.glfw_window:
            self._cleanup()
            raise RuntimeError("Unable to create GLFW window")

        glfw.make_context_current(self.glfw_window)
        self.gl_context.bind()

        # set some initial OpenGL state
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glFrontFace(GL.GL_CCW)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glBlendEquation(GL.GL_FUNC_ADD)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(0)

        glfw.set_window_size_callback(self.glfw_window, self.on_resize)

        self.set_clear_color(color.BLACK)

        self.initialized = True

        return self

    def set_resize_callback(self, callback: Callable[..., None]) -> None:
        self.on_resize = callback
        if self.initialized:
            glfw.set_window_size_callback(self.glfw_window, self.on_resize)

    def set_clear_color(self, col: color.Color) -> None:
        self.clear_color = col
        GL.glClearColor(col.r, col.g, col.b, col.a)

    @staticmethod
    def set_viewport(x: int, y: int, w: int, h: int) -> None:
        GL.glViewport(int(x), int(y), int(w), int(h))
        Window.viewport = Rect(x, y, w, h)

    def clear(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _cleanup(self) -> None:
        glfw.terminate()