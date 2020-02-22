from OpenGL import GL

from .framebuffer import Framebuffer
from .shader import Shader
from . import mesh

_VERTEX_SHADER = """#version 330 core

layout (location = 0) in vec3 in_Pos;
layout (location = 2) in vec2 in_UV;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(in_Pos.x, in_Pos.y, 0.0, 1.0);
    TexCoords = in_UV;
}
"""

_FRAGMENT_SHADER = """#version 330 core

out vec4 out_FragColor;

in vec2 TexCoords;

uniform sampler2D FramebufferTexture;

void main()
{
    out_FragColor = texture(FramebufferTexture, TexCoords);
}
"""


class UpscaleSurface:
    def __init__(self, width: int, height: int) -> None:
        self.shader = Shader("_upscalesurface", {
            "vertex": _VERTEX_SHADER,
            "fragment": _FRAGMENT_SHADER
        })
        self.framebuffer = Framebuffer(width, height, GL.GL_FRAMEBUFFER)
        self.quad_mesh = mesh.make_quad()

    def begin(self) -> None:
        self.framebuffer.bind()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def end(self) -> None:
        self.framebuffer.unbind()

    def render(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glDisable(GL.GL_DEPTH_TEST)
        self.shader.bind()
        self.framebuffer.get_texture(0).bind()
        self.quad_mesh.render()
        self.framebuffer.get_texture(0).unbind()
        self.shader.unbind()
        GL.glEnable(GL.GL_DEPTH_TEST)