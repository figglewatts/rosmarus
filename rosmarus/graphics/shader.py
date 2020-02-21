from typing import Mapping

from OpenGL import GL
import glm

VERTEX = "vertex"
FRAGMENT = "fragment"

SHADER_TYPE_MAP = {
    VERTEX: GL.GL_VERTEX_SHADER,
    FRAGMENT: GL.GL_FRAGMENT_SHADER
}


class Shader:
    def __init__(self, name: str, shaders: Mapping[str, str]) -> None:
        self.name = name
        self._handles = {}
        self._uniform_locations = {}
        self._program = GL.GLuint(0)
        self._compile_and_link(shaders)

    def set_bool(self, name: str, value: bool) -> None:
        GL.glUniform1i(self._get_location(name), value)

    def set_int(self, name: str, value: int) -> None:
        GL.glUniform1i(self._get_location(name), value)

    def set_float(self, name: str, value: float) -> None:
        GL.glUniform1f(self._get_location(name), value)

    def set_mat4(self,
                 name: str,
                 value: glm.mat4,
                 transpose: bool = False) -> None:
        GL.glUniformMatrix4fv(self._get_location(name), 1, transpose,
                              glm.value_ptr(value))

    def set_mat3(self,
                 name: str,
                 value: glm.mat3,
                 transpose: bool = False) -> None:
        GL.glUniformMatrix3fv(self._get_location(name), 1, transpose,
                              glm.value_ptr(value))

    def set_vec2(self, name: str, value: glm.vec2) -> None:
        GL.glUniform2fv(self._get_location(name), 1, glm.value_ptr(value))

    def set_vec3(self, name: str, value: glm.vec3) -> None:
        GL.glUniform3fv(self._get_location(name), 1, glm.value_ptr(value))

    def set_vec4(self, name: str, value: glm.vec4) -> None:
        GL.glUniform4fv(self._get_location(name), 1, glm.value_ptr(value))

    def _compile_and_link(self, shaders: Mapping[str, str]) -> None:
        for shader_type, shader_source in shaders.items():
            self._compile_shader(shader_type, shader_source)

        self._program = GL.glCreateProgram()
        for _, handle in self._handles.items():
            GL.glAttachShader(self._program, handle)
        GL.glLinkProgram(self._program)
        _check_link_err(self._program, self.name)

    def _compile_shader(self, shader_type: str, shader_source: str) -> None:
        if shader_type not in SHADER_TYPE_MAP.keys():
            raise ValueError(f"Invalid shader type '{shader_type}'")

        if shader_type in self._handles:
            raise ValueError(
                f"Cannot compile multiple shaders of type '{shader_type}'")

        handle = GL.glCreateShader(SHADER_TYPE_MAP[shader_type])
        self._handles[shader_type] = handle
        GL.glShaderSource(handle, shader_source)
        GL.glCompileShader(handle)
        _check_compile_err(handle, self.name)

    def _get_location(self, name: str) -> GL.GLuint:
        if name in self._uniform_locations:
            return self._uniform_locations[name]

        location = GL.glGetUniformLocation(self._program, name)
        if location == -1:
            return -1
        self._uniform_locations[name] = location
        return location

    def bind(self) -> None:
        GL.glUseProgram(self._program)

    def unbind(self) -> None:
        GL.glUseProgram(0)

    def cleanup(self) -> None:
        for handle in self._handles.values():
            GL.glDeleteShader(handle)
        GL.glDeleteProgram(self._program)


def _check_compile_err(shader: GL.GLuint, name: str) -> None:
    success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if success == GL.GL_FALSE:
        err_log = GL.glGetShaderInfoLog(shader)
        raise RuntimeError(
            f"Error compiling shader '{name}', error: {err_log}")


def _check_link_err(program: GL.GLuint, name: str) -> None:
    success = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if success == GL.GL_FALSE:
        err_log = GL.glGetProgramInfoLog(program)
        raise RuntimeError(f"Error linking shader '{name}', error: {err_log}")