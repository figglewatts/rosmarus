import yaml

from .. import resources
from ..graphics.shader import Shader


def load_shader(path: str) -> Shader:
    with open(path, "r") as shader_file:
        raw_shader = yaml.safe_load(shader_file.read())

        name = raw_shader.get("name", None)
        shaders = raw_shader.get("shaders", None)

        if name is None or shaders is None:
            raise RuntimeError(
                "Unable to load shader '{path}', missing 'name' or 'shaders' field"
            )

        return Shader(name, shaders)


def cleanup_shader(shader: Shader) -> Shader:
    shader.cleanup()


resources.register_type_handler("shader", load_shader, cleanup_shader)