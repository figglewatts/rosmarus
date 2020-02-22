import glm

from ..math.transform import Transform


class Camera:
    def __init__(self):
        self.transform = Transform()

    def view_matrix(self) -> glm.mat4:
        return glm.lookAt(
            self.transform.get_position(),
            self.transform.get_position() + self.transform.forward(),
            self.transform.up())
