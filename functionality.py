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
from rosmarus.render.sprite import Sprite
from rosmarus.render.spritesheet import SpriteSheet
from rosmarus import scene
import rosmarus.log


class TestScene(scene.Scene):
    def on_active(self):
        pass

    def init(self):
        self.poke_tex: Texture2D = resources.load("texture",
                                                  "textures/pokemon.png",
                                                  mipmap=None)
        self.sprsh = SpriteSheet(self.poke_tex, 16, 16)
        self.cam = Camera(
            glm.ortho(0, self.window.width, 0, self.window.height, 0.01, 100))
        self.cam.transform.translate(glm.vec3(0, 0, 1))
        self.sb = SpriteBatch(self.cam)
        self.spr_count_x, _ = self.sprsh.get_size_in_sprites()

    def render(self, *args, **kwargs):
        self.sb.begin()

        for y in range(0, 16):
            for x in range(0, 16):
                idx = y * self.spr_count_x + x
                self.sprsh.get_sprite(idx, x_pos=x * 20 + 8,
                                      y_pos=y * 20 + 8).draw(self.sb)

        self.sb.end()

    def update(self, delta_time, *args, **kwargs):
        pass


TARGET_WIDTH = 200
TARGET_HEIGHT = 150


def main():
    app = Application("Rosmarus test")
    rosmarus.log.init(app)
    with app.make_window(TARGET_WIDTH * 4, TARGET_HEIGHT * 4,
                         (4, 3)) as window:
        window.set_clear_color(color.BLACK)
        uss = UpscaleSurface(TARGET_WIDTH, TARGET_HEIGHT)

        app.scene_manager.add_scene(TestScene(window, "test", active=True))

        def resize(win, w, h) -> None:
            window.clear()
            target_aspect = float(TARGET_WIDTH) / float(TARGET_HEIGHT)

            width = w
            height = int(width / target_aspect + 0.5)
            if height > h:
                height = h
                width = int(height * target_aspect + 0.5)

            x_pos = (w / 2) - (width / 2)
            y_pos = (h / 2) - (height / 2)

            print(x_pos, y_pos)
            print(width, height)

            window.set_viewport(x_pos, y_pos, width, height)

        def render() -> None:
            uss.begin()
            window.clear()
            app.scene_manager.render()
            uss.end()

            uss.render()

        def update(delta_time: float) -> None:
            app.scene_manager.update(delta_time)

        app.set_render_callback(render)
        app.set_update_callback(update)
        window.set_resize_callback(resize)

        app.main_loop(window)


if __name__ == "__main__":
    main()