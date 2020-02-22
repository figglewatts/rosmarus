from ctypes import *
from typing import List

from OpenGL import GL

from .vertex import Vertex


class Mesh:
    def __init__(self, verts: List[Vertex], indices: List[int]) -> None:
        self.has_data = False
        self.set_data(verts, indices)

    def set_data(self, verts: List[Vertex], indices: List[int]) -> None:
        if self.has_data:
            self.cleanup()

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        self.vertices = (Vertex * len(verts))(*verts)
        self.indices = (c_uint32 * len(indices))(*indices)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, sizeof(self.vertices),
                        byref(self.vertices), GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, sizeof(self.indices),
                        byref(self.indices), GL.GL_STATIC_DRAW)

        # position
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 4, GL.GL_FLOAT, GL.GL_FALSE,
                                 sizeof(Vertex), c_void_p(0))

        # normals
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT,
                                 GL.GL_FALSE, sizeof(Vertex),
                                 c_void_p(Vertex.normal.offset))

        # uvs
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE,
                                 sizeof(Vertex), c_void_p(Vertex.uv.offset))

        # color
        GL.glEnableVertexAttribArray(3)
        GL.glVertexAttribPointer(3, 4, GL.GL_FLOAT, GL.GL_FALSE,
                                 sizeof(Vertex), c_void_p(Vertex.color.offset))

        GL.glBindVertexArray(0)

        self.has_data = True

    def bind(self) -> None:
        GL.glBindVertexArray(self.vao)

    def unbind(self) -> None:
        GL.glBindVertexArray(0)

    def render(self) -> None:
        self.bind()
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices),
                          GL.GL_UNSIGNED_INT, None)
        self.unbind()

    def cleanup(self) -> None:
        GL.glDeleteBuffers(1, self.vbo)
        GL.glDeleteBuffers(1, self.ebo)
        GL.glDeleteVertexArrays(1, self.vao)


def make_quad() -> Mesh:
    return Mesh([
        Vertex((-1, -1, -1, 1), uv=(0, 0)),
        Vertex((-1, 1, -1, 1), uv=(0, 1)),
        Vertex((1, 1, -1, 1), uv=(1, 1)),
        Vertex((1, -1, -1, 1), uv=(1, 0))
    ], [0, 2, 1, 0, 3, 2])