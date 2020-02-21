import glfw


class GLContext:
    def __init__(self, major_version: int, minor_version: int) -> None:
        self.major_version = major_version
        self.minor_version = minor_version

    def bind(self) -> None:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.major_version)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.minor_version)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
