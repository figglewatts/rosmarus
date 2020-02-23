import logging
import uuid

import glm
from OpenGL import GL

from ..graphics.mesh import Mesh
from ..graphics.shader import Shader
from ..graphics.texture import Texture2D
from ..graphics import color
from ..math.transform import Transform


class Renderable:
    def __init__(self,
                 mesh: Mesh,
                 shader: Shader,
                 texture: Texture2D,
                 transform: Transform = Transform(),
                 transparent: bool = False) -> None:
        self.mesh = mesh
        self.shader = shader
        self.texture = texture
        self.transform = transform
        self.tint = color.WHITE
        self.id = uuid.uuid4()
        self.active = True
        self.transparent = transparent

    def set_active(self, state: bool) -> None:
        self.active = state

    def set_tint(self, col: color.Color) -> None:
        self.tint = col

    def draw(self,
             view_matrix: glm.mat4,
             proj_matrix: glm.mat4,
             elements: int = -1) -> None:
        if not self.active:
            return

        if self.mesh is None or self.shader is None:
            logging.warning("Cannot draw renderable with no Mesh or no Shader")
            return

        self.shader.bind()
        self.shader.set_mat4("ModelMatrix", self.transform.matrix())
        self.shader.set_mat4("ViewMatrix", view_matrix)
        self.shader.set_mat4("ProjectionMatrix", proj_matrix)
        self.shader.set_vec4("TintColor", self.tint.to_vec4())
        self.texture.bind()
        self.mesh.render(elements)
        self.texture.unbind()
        self.shader.unbind()
