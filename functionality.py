import glfw
import glm
from OpenGL import GL
import OpenGL_accelerate
from OpenGL.GL.shaders import compileProgram, compileShader

from rosmarus.graphics.gl_context import GLContext
from rosmarus.graphics.window import Window
from rosmarus.graphics.vertex import Vertex
from rosmarus.graphics import mesh
from rosmarus.graphics.shader import Shader
from rosmarus import resources
from rosmarus import io
from rosmarus.math import transform
from rosmarus.graphics.camera import Camera
from rosmarus.graphics.upscale_surface import UpscaleSurface
from rosmarus.graphics.texture import Texture2D


def main():
    ctx = GLContext(4, 3)
    with Window("Rosmarus", 800, 600, ctx) as window:
        m = mesh.make_quad()
        t = transform.Transform2D()
        shader: Shader = resources.load(
            "shader", "functionality_data/shaders/main.shader")

        shader.bind()
        t.translate((80, 80))
        t.set_scale(glm.vec2(32, 32))

        tex: Texture2D = resources.load(
            "texture", "functionality_data/textures/dat_boi.png")

        cam = Camera()
        cam.transform.translate(glm.vec3(0, 0, 1))
        shader.set_mat4("ViewMatrix", cam.view_matrix())

        proj_m = glm.ortho(0, window.width, 0, window.height, 0.01, 100)
        shader.set_mat4("ProjectionMatrix", proj_m)
        shader.unbind()

        uss = UpscaleSurface(window.width / 4, window.height / 4)

        GL.glClearColor(1, 0, 0, 1)

        while not glfw.window_should_close(window.glfw_window):
            uss.begin()
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            shader.bind()
            tex.bind()
            t.rotate(0.001, False)
            shader.set_mat4("ModelMatrix", t.matrix())
            m.render()
            tex.unbind()
            shader.unbind()
            uss.end()

            uss.render()

            glfw.swap_buffers(window.glfw_window)
            glfw.poll_events()


if __name__ == "__main__":
    main()