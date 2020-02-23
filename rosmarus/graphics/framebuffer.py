from dataclasses import dataclass
from typing import List, Tuple

from OpenGL import GL

from .texture import Texture2D


class Framebuffer:
    def __init__(self,
                 width: int,
                 height: int,
                 fb_type: GL.GLenum,
                 color_attachments: List[Texture2D] = None,
                 depth_attachment: Texture2D = None) -> None:
        self._width = width
        self._height = height
        self._type = fb_type
        self._handle = GL.glGenFramebuffers(1)
        self._color_attachments = []
        if color_attachments is None:
            color_attachments = [Texture2D(width, height, mipmap=False)]
        for color_attachment in color_attachments:
            self.add_color_attachment(color_attachment)
        self._depth_attachment = None
        if depth_attachment is None:
            depth_attachment = Texture2D(
                width,
                height,
                internal_format=GL.GL_DEPTH_COMPONENT32,
                color_format=GL.GL_DEPTH_COMPONENT,
                data_type=GL.GL_UNSIGNED_INT)
        self.set_depth_attachment(depth_attachment)

    def _create(self) -> None:
        self.bind()

        color_attachments = (GL.GLenum * len(self._color_attachments))(*[
            GL.GL_COLOR_ATTACHMENT0 + i
            for i in range(0, len(self._color_attachments))
        ])
        GL.glDrawBuffers(len(self._color_attachments), color_attachments)

        status = GL.glCheckFramebufferStatus(self._type)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Error creating framebuffer")

        self.unbind()

    def add_color_attachment(self, attachment: Texture2D) -> None:
        self.bind()
        GL.glFramebufferTexture2D(
            self._type, GL.GL_COLOR_ATTACHMENT0 + len(self._color_attachments),
            GL.GL_TEXTURE_2D, attachment.get_handle(), 0)
        self.unbind()
        self._color_attachments.append(attachment)

    def set_depth_attachment(self, attachment: Texture2D) -> None:
        self.bind()
        GL.glFramebufferTexture2D(self._type, GL.GL_DEPTH_ATTACHMENT,
                                  GL.GL_TEXTURE_2D, attachment.get_handle(), 0)
        self.unbind()
        self._depth_attachment = attachment

    def cleanup(self) -> None:
        for color_attachment in self._color_attachments:
            color_attachment.cleanup()

        if self._depth_attachment is not None:
            self._depth_attachment.cleanup()

        GL.glDeleteFramebuffers(1, self._handle)

    def get_size(self) -> Tuple[int, int]:
        return self._width, self._height

    def get_handle(self) -> GL.GLuint:
        return self._handle

    def get_texture(self, index: int) -> Texture2D:
        return self._color_attachments[index]

    def get_depth_texture(self) -> Texture2D:
        return self._depth_attachment

    def bind(self) -> None:
        GL.glBindFramebuffer(self._type, self._handle)

    def unbind(self) -> None:
        GL.glBindFramebuffer(self._type, 0)

    def resize(self, width: int, height: int) -> None:
        # recreate all of the color attachments with the new size
        for color_attachment in self._color_attachments:
            color_attachment.resize(width, height)

        if self._depth_attachment is not None:
            self._depth_attachment.resize(width, height)

        self._width = width
        self._height = height