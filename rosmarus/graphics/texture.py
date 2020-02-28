from __future__ import annotations
from ctypes import c_void_p, byref
from typing import Tuple

from OpenGL import GL

from ..math.rect import Rect


class Texture2D:
    def __init__(self,
                 width: int,
                 height: int,
                 data: c_void_p = None,
                 internal_format: GL.GLint = GL.GL_RGBA8,
                 color_format: GL.GLenum = GL.GL_RGBA,
                 data_type: GL.GLenum = GL.GL_UNSIGNED_BYTE,
                 min_filter: GL.GLint = GL.GL_NEAREST,
                 mag_filter: GL.GLint = GL.GL_NEAREST,
                 s_wrap: GL.GLint = GL.GL_CLAMP_TO_EDGE,
                 t_wrap: GL.GLint = GL.GL_CLAMP_TO_EDGE,
                 mipmap: bool = True) -> None:
        self._width = width
        self._height = height
        self._handle = GL.glGenTextures(1)
        self._internal_format = internal_format
        self._color_format = color_format
        self._data_type = data_type
        self._mipmap = mipmap
        self._data = data
        self.bind()
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, internal_format, self._width,
                        self._height, 0, color_format, data_type, data)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                           min_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                           mag_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, s_wrap)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, t_wrap)
        if mipmap:
            GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        self.unbind()

    def get_size(self) -> Tuple[int, int]:
        return self._width, self._height

    def resize(self, width: int, height: int) -> None:
        self.bind()
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, self._internal_format, width,
                        height, 0, self._color_format, self._data_type,
                        self._data)
        self._width = width
        self._height = height
        self.unbind()

    def set_data(self, data: c_void_p) -> None:
        self.bind()
        GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, self._width,
                           self._height, self._color_format, self._data_type,
                           data)
        self._data = data
        if self._mipmap:
            GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        self.unbind()

    def region_to_uvs(self, region: Rect) -> Rect:
        u = region.x / self._width
        v = region.y / self._height
        u2 = region.x2 / self._width
        v2 = region.y2 / self._height
        return Rect(u, v, u2 - u, v2 - v)

    def bind(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._handle)

    def unbind(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def cleanup(self) -> None:
        GL.glDeleteTextures(1, GL.GLuint(self._handle))

    def get_handle(self) -> GL.GLuint:
        return self._handle

    def __eq__(self, other: Texture2D) -> bool:
        if isinstance(other, Texture2D):
            return self._handle == other._handle
        return False