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
from rosmarus.graphics import color
from rosmarus.application import Application
from rosmarus.render.spritebatch import SpriteBatch
import rosmarus.log


def main():
    app = Application("Rosmarus test")
    rosmarus.log.init(app)
    with app.make_window(800, 600, (4, 3)) as window:
        tex: Texture2D = resources.load("texture", "textures/dat_boi.png")

        window.set_clear_color(color.BLUE)

        cam = Camera()
        cam.transform.translate(glm.vec3(0, 0, 1))

        proj_m = glm.ortho(0, window.width, 0, window.height, 0.01, 100)

        sb = SpriteBatch(projection_matrix=proj_m)
        sb.set_camera(cam)

        uss = UpscaleSurface(window.width / 4, window.height / 4)

        def render() -> None:
            uss.begin()
            window.clear()
            sb.begin()
            sb.draw(tex, 128, 128, width=32, height=32, tint=color.RED)
            sb.draw(tex, 64, 128, width=32, height=32)
            sb.draw(tex, 32, 32, width=32, height=32)
            sb.draw(tex, 0, 128, width=32, height=32)
            sb.end()
            uss.end()

            uss.render()

        app.set_render_callback(render)

        app.main_loop(window)


if __name__ == "__main__":
    main()