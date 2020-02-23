from __future__ import annotations

import glfw
from OpenGL import GL

from .gl_context import GLContext
from . import color


class Window:
    def __init__(self, title: str, width: int, height: int,
                 gl_context: GLContext) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.gl_context = gl_context

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

        self.set_clear_color(color.BLACK)

        return self

    def set_clear_color(self, col: color.Color) -> None:
        self.clear_color = col
        GL.glClearColor(col.r, col.g, col.b, col.a)

    def clear(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _cleanup(self) -> None:
        glfw.terminate()