from itertools import repeat

import glm
from OpenGL import GL

from ..graphics.vertex import Vertex
from ..graphics.mesh import Mesh
from ..graphics.shader import Shader
from ..graphics.camera import Camera
from .renderable import Renderable
from ..math.transform import Transform2D
from ..graphics.texture import Texture2D
from ..graphics import color

_SB_VERTEX_SHADER = """#version 330 core

layout (location = 0) in vec3 in_Pos;
layout (location = 2) in vec2 in_UV;
layout (location = 3) in vec4 in_Color;

uniform mat4 ModelMatrix;
uniform mat4 ViewMatrix;
uniform mat4 ProjectionMatrix;

out vec2 TexCoords;
out vec4 VertexColor;

void main()
{
    gl_Position = ProjectionMatrix * ViewMatrix * ModelMatrix * vec4(in_Pos, 1.0);
    TexCoords = in_UV;
    VertexColor = in_Color;
}
"""

_SB_FRAGMENT_SHADER = """#version 330 core

out vec4 out_FragColor;

in vec2 TexCoords;
in vec4 VertexColor;

uniform sampler2D Tex;
uniform vec4 TintColor;

void main()
{
    out_FragColor = texture(Tex, TexCoords) * TintColor * VertexColor;
}
"""


class SpriteBatch:
    def __init__(
            self,
            projection_matrix: glm.mat4,
            size: int = 1024,
            transform: Transform2D = Transform2D()) -> None:
        self.size = size
        self.length = size * 4  # 4 verts per size

        verts = list(repeat(Vertex(glm.vec4(0, 0, 0, 0)), self.length))
        indices = [i for i in range(0, size * 6)]  # 2 tris per sprite

        self.renderable = Renderable(
            Mesh(verts, indices, usage=GL.GL_DYNAMIC_DRAW),
            Shader("_sb_shader", {
                "vertex": _SB_VERTEX_SHADER,
                "fragment": _SB_FRAGMENT_SHADER
            }), transform)
        self.vertices, self.indices = self.renderable.mesh.get_data()

        self.camera = None
        self.projection_matrix = projection_matrix

        self.drawing = False
        self.render_calls = 0
        self.vertices_drawn = 0
        self.indices_drawn = 0
        self._inv_tex_dimensions = (0, 0)

    def begin(self) -> None:
        if self.drawing:
            raise RuntimeError(
                "Cannot begin SpriteBatch again, it is already drawing")

        self.render_calls = 0
        self.drawing = True

    def end(self) -> None:
        if not self.drawing:
            raise RuntimeError(
                "Cannot end SpriteBatch, it has not yet been started")

        if self.vertices_drawn > 0:
            self.flush()

        self.drawing = False

    def set_camera(self, cam: Camera) -> None:
        self.camera = cam

    def set_projection(self, matrix: glm.mat4) -> None:
        self.projection_matrix = matrix

    def flush(self) -> None:
        if self.vertices_drawn == 0:
            return

        if self.camera is None:
            raise RuntimeError(
                "Cannot flush SpriteBatch without setting its Camera")

        self.render_calls += 1
        self.renderable.mesh.reupload_data()

        sprite_count = self.vertices_drawn / 4  # 4 verts per sprite
        self.renderable.draw(self.camera.view_matrix(),
                             self.projection_matrix,
                             elements=int(sprite_count *
                                          6))  # 6 indices per sprite

        self.vertices_drawn = 0
        self.indices_drawn = 0

    def draw(self,
             tex: Texture2D,
             x_pos: int,
             y_pos: int,
             scale_x: int = 1,
             scale_y: int = 1,
             width: int = -1,
             height: int = -1,
             rotation: float = 0,
             tint: color.Color = color.WHITE) -> None:
        if tex != self.renderable.texture:
            self._switch_texture(tex)

        if self.vertices_drawn + 4 > self.length:
            self.flush()

        t_width, t_height = tex.get_size()
        if width == -1:
            width = t_width
        if height == -1:
            height = t_height

        u, v = (0, 0)
        u2, v2 = (1, 1)
        x, y = -(width / 2), -(height / 2)
        x2, y2 = x + width, y + height

        trans = Transform2D()

        if rotation != 0:
            trans.rotate(rotation, False)

        if scale_x != 1 or scale_y != 1:
            trans.set_scale((scale_x, scale_y))

        trans.set_position((x_pos, y_pos))

        tint_col = tint.to_vec4()

        # create the vertices
        v0 = Vertex(trans.matrix() * glm.vec4(x, y, -1, 1),
                    uv=glm.vec2(u, v),
                    color=tint_col)
        v1 = Vertex(trans.matrix() * glm.vec4(x, y2, -1, 1),
                    uv=glm.vec2(u, v2),
                    color=tint_col)
        v2 = Vertex(trans.matrix() * glm.vec4(x2, y2, -1, 1),
                    uv=glm.vec2(u2, v2),
                    color=tint_col)
        v3 = Vertex(trans.matrix() * glm.vec4(x2, y, -1, 1),
                    uv=glm.vec2(u2, v),
                    color=tint_col)

        # add the vertices to the mesh data
        self.vertices[self.vertices_drawn] = v0
        self.vertices[self.vertices_drawn + 1] = v1
        self.vertices[self.vertices_drawn + 2] = v2
        self.vertices[self.vertices_drawn + 3] = v3

        # add the indices to the mesh data -- 2 tris, indices: (0 2 1), (0 3 2)
        self.indices[self.indices_drawn] = self.vertices_drawn
        self.indices[self.indices_drawn + 1] = self.vertices_drawn + 2
        self.indices[self.indices_drawn + 2] = self.vertices_drawn + 1
        self.indices[self.indices_drawn + 3] = self.vertices_drawn
        self.indices[self.indices_drawn + 4] = self.vertices_drawn + 3
        self.indices[self.indices_drawn + 5] = self.vertices_drawn + 2

        # update counts
        self.vertices_drawn += 4
        self.indices_drawn += 6

    def _switch_texture(self, tex: Texture2D) -> None:
        self.flush()
        self.renderable.texture = tex
        self._inv_tex_dimensions = tuple(1.0 / dim for dim in tex.get_size())