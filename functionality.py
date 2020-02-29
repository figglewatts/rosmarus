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
from rosmarus.graphics.viewport import ConstantViewport
from rosmarus import scene
import rosmarus.log
from rosmarus import controls
from rosmarus.controls import InputState
from rosmarus import audio
from rosmarus.render.tiles import TileMap, Tile


class TestScene(scene.Scene):
    def on_active(self):
        pass

    def init(self):
        self.poke_tex: Texture2D = resources.load("texture",
                                                  "textures/pokemon.png",
                                                  mipmap=None)
        self.sprsh = SpriteSheet(self.poke_tex, 16, 16)
        self.tilemap = TileMap(self.sprsh,
                               14,
                               12,
                               14,
                               10,
                               position=glm.vec2(8, 8))
        self.tilemap.fill(Tile(7))
        self.tilemap[0, 0] = Tile(8)
        self.cam = Camera(
            glm.ortho(0, TARGET_WIDTH, 0, TARGET_HEIGHT, 0.01, 100))
        self.cam.transform.translate(glm.vec3(0, 0, 1))
        self.sb = SpriteBatch(self.cam)

        self.test_audio: audio.AudioStream = resources.load(
            "sound", "audio/pulsar-lullaby-short.ogg")

        audio.play(self.test_audio, loop=False)

        controls.add("up", glfw.KEY_W)
        controls.add("down", glfw.KEY_S)
        controls.add("left", glfw.KEY_A)
        controls.add("right", glfw.KEY_D)

    def render(self, *args, **kwargs):
        self.sb.begin()
        self.tilemap.draw(self.sb)
        self.sb.end()

    def update(self, delta_time, *args, **kwargs):
        if controls.check("up", InputState.HELD):
            self.cam.transform.translate(glm.vec3(0, 1, 0))
        elif controls.check("down", InputState.HELD):
            self.cam.transform.translate(glm.vec3(0, -1, 0))

        if controls.check("left", InputState.HELD):
            self.cam.transform.translate(glm.vec3(-1, 0, 0))
        elif controls.check("right", InputState.HELD):
            self.cam.transform.translate(glm.vec3(1, 0, 0))


TARGET_WIDTH = 200
TARGET_HEIGHT = 150


def main():
    app = Application("Rosmarus test")
    rosmarus.log.init(app)
    with app.make_window(TARGET_WIDTH * 4, TARGET_HEIGHT * 4,
                         (4, 3)) as window:
        window.set_clear_color(color.RED)
        viewport = ConstantViewport(window, TARGET_WIDTH, TARGET_HEIGHT)
        uss = UpscaleSurface(TARGET_WIDTH, TARGET_HEIGHT, viewport)

        app.scene_manager.add_scene(TestScene(window, "test", active=True))

        controls.add("test", glfw.KEY_W)

        def resize(win, w, h) -> None:
            viewport.on_resize(w, h)

        def render() -> None:
            uss.begin()
            window.clear()
            app.scene_manager.render()
            uss.end()
            uss.render()

        def update(delta_time: float) -> None:
            controls.handle()
            app.scene_manager.update(delta_time)

        app.set_render_callback(render)
        app.set_update_callback(update)
        window.set_resize_callback(resize)

        app.main_loop(window)


if __name__ == "__main__":
    main()