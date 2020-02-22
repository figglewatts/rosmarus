import glfw
import glm
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from rosmarus.graphics.gl_context import GLContext
from rosmarus.graphics.window import Window
from rosmarus.graphics.vertex import Vertex
from rosmarus.graphics.mesh import Mesh
from rosmarus.graphics.shader import Shader
from rosmarus import resources
from rosmarus.io import shader_handler
from rosmarus.math import transform
from rosmarus.graphics.camera import Camera

QUAD_VERTS = [
    Vertex((0, 0, -1, 1)),
    Vertex((0, 1, -1, 1)),
    Vertex((1, 1, -1, 1)),
    Vertex((1, 0, -1, 1))
]

QUAD_INDICES = [0, 2, 1, 0, 3, 2]


def main():
    ctx = GLContext(4, 3)
    with Window("Rosmarus", 800, 600, ctx) as window:
        mesh = Mesh(QUAD_VERTS, QUAD_INDICES)

        shader: Shader = resources.load(
            "shader", "functionality_data/shaders/main.shader")

        shader.bind()
        t = transform.Transform2D()
        t.translate((-1, 0))

        cam = Camera()
        cam.transform.translate(glm.vec3(0, 0, 1))
        shader.set_mat4("ViewMatrix", cam.view_matrix())

        proj_m = glm.perspective(glm.radians(90), 800 / 600, 0.01, 100)
        shader.set_mat4("ProjectionMatrix", proj_m)

        while not glfw.window_should_close(window.glfw_window):
            GL.glClearColor(1, 0, 0, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            t.rotate(0.001, False)
            shader.set_mat4("ModelMatrix", t.matrix())
            mesh.render()

            glfw.swap_buffers(window.glfw_window)
            glfw.poll_events()


if __name__ == "__main__":
    main()