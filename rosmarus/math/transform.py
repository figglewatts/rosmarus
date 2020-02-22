from __future__ import annotations

import glm


class Transform2D:
    def __init__(self):
        self._position = glm.vec2(0)
        self._scale = glm.vec2(1)
        self._orientation = glm.quat()
        self._matrix = glm.mat4()
        self._matrix_dirty = False
        self._parent = None

    def get_position(self) -> glm.vec2:
        return self._position

    def world_position(self) -> glm.vec2:
        return self._position if self._parent is None \
            else self._parent.matrix() * glm.vec4(self._position, 0, 1)

    def _recompute_matrix(self) -> None:
        # if we have a parent set it to that first
        if self._parent is not None:
            self._matrix = self._parent.matrix()
        else:
            self._matrix = glm.mat4()

        # now compute the matrix
        self._matrix = self._matrix * glm.translate(
            glm.mat4(), glm.vec3(self._position, 0)) * glm.mat4_cast(
                self._orientation) * glm.scale(glm.mat4(),
                                               glm.vec3(self._scale, 1))
        self._matrix_dirty = False

    def set_position(self, position: glm.vec2) -> None:
        self._position = position
        self._matrix_dirty = True

    def set_scale(self, scale: glm.vec2) -> None:
        # if the length is equal to zero, do nothing
        # we don't want to scale to zero
        sqr_len = glm.dot(scale, scale)
        if glm.epsilonEqual(sqr_len, 0, glm.epsilon()):
            return

        self._scale = scale
        self._matrix_dirty = True

    def set_orientation(self, orientation: float) -> None:
        self._orientation = glm.angleAxis(orientation, glm.vec3(0, 0, 1))
        self._matrix_dirty = True

    def up(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(0, 1, 0))

    def forward(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(0, 0, -1))

    def right(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(1, 0, 0))

    def matrix(self) -> glm.mat4:
        if self._matrix_dirty:
            self._recompute_matrix()
        return self._matrix

    def to_world(self, position: glm.vec2) -> glm.vec2:
        world_pos = glm.vec4(position, 0, 1) * self.matrix()
        return glm.vec2(world_pos)

    def to_local(self, position: glm.vec2) -> glm.vec2:
        local_pos = glm.vec4(position, 0, 1) * glm.inverse(self.matrix())
        return glm.vec2(local_pos)

    def set_parent(self, parent: Transform) -> None:
        self._parent = parent
        self._matrix_dirty = True

    def translate(self, v: glm.vec2) -> Transform:
        self._matrix = glm.translate(glm.mat4(), glm.vec3(v, 0)) * self._matrix
        self._position += v
        return self

    def rescale(self, scale: glm.vec2) -> Transform:
        self._matrix = glm.scale(glm.mat4(), glm.vec3(scale, 1)) * self._matrix
        self._scale *= scale
        return self

    def rotate(self, rot: float, local: bool) -> Transform:
        if local:
            rot_mat = glm.mat4_cast(glm.angleAxis(rot, glm.vec3(0, 0, 1)))
            self._matrix = rot_mat * self._matrix
            self._orientation = self._orientation * rot
        else:
            rot_mat = glm.mat4_cast(glm.angleAxis(rot, glm.vec3(0, 0, 1)))
            self._matrix = self._matrix * rot_mat
            self._orientation = rot * self._orientation
        return self


class Transform:
    def __init__(self):
        self._position = glm.vec3(0)
        self._scale = glm.vec3(1)
        self._orientation = glm.quat()
        self._matrix = glm.mat4()
        self._matrix_dirty = False
        self._parent = None

    def get_position(self) -> glm.vec3:
        return self._position

    def world_position(self) -> glm.vec3:
        return self._position if self._parent is None \
            else self._parent.matrix() * glm.vec4(self._position, 1)

    def _recompute_matrix(self) -> None:
        # if we have a parent set it to that first
        if self._parent is not None:
            self._matrix = self._parent.matrix()
        else:
            self._matrix = glm.mat4()

        # now compute the matrix
        self._matrix = self._matrix * glm.translate(
            glm.mat4(), self._position) * glm.mat4_cast(
                self._orientation) * glm.scale(glm.mat4(), self._scale)
        self._matrix_dirty = False

    def set_position(self, position: glm.vec3) -> None:
        self._position = position
        self._matrix_dirty = True

    def set_scale(self, scale: glm.vec3) -> None:
        # if the length is equal to zero, do nothing
        # we don't want to scale to zero
        sqr_len = glm.dot(scale, scale)
        if glm.epsilonEqual(sqr_len, 0, glm.epsilon()):
            return

        self._scale = scale
        self._matrix_dirty = True

    def set_orientation(self, orientation: glm.quat) -> None:
        self._orientation = orientation
        self._matrix_dirty = True

    def up(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(0, 1, 0))

    def forward(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(0, 0, -1))

    def right(self) -> glm.vec3:
        return glm.normalize(glm.quat_cast(self.matrix()) * glm.vec3(1, 0, 0))

    def matrix(self) -> glm.mat4:
        if self._matrix_dirty:
            self._recompute_matrix()
        return self._matrix

    def to_world(self, position: glm.vec3) -> glm.vec3:
        world_pos = glm.vec4(position, 1) * self.matrix()
        return glm.vec3(world_pos)

    def to_local(self, position: glm.vec3) -> glm.vec3:
        local_pos = glm.vec4(position, 1) * glm.inverse(self.matrix())
        return glm.vec3(local_pos)

    def set_parent(self, parent: Transform) -> None:
        self._parent = parent
        self._matrix_dirty = True

    def translate(self, v: glm.vec3) -> Transform:
        self._matrix = glm.translate(glm.mat4(), v) * self._matrix
        self._position += v
        return self

    def rescale(self, scale: glm.vec3) -> Transform:
        self._matrix = glm.scale(glm.mat4(), scale) * self._matrix
        self._scale *= scale
        return self

    def rotate(self, rot: glm.quat, local: bool) -> Transform:
        if local:
            rot_mat = glm.mat4_cast(rot)
            self._matrix = rot_mat * self._matrix
            self._orientation = self._orientation * rot
        else:
            rot_mat = glm.mat4_cast(rot)
            self._matrix = self._matrix * rot_mat
            self._orientation = rot * self._orientation
        return self

    def rotate_euler(self, euler: glm.vec3, local: bool) -> Transform:
        rot = glm.quat(euler)
        return self.rotate(rot, local)

    def rotate_axis(self, angle: float, axis: glm.vec3,
                    local: bool) -> Transform:
        rot = glm.angleAxis(angle, axis)
        return self.rotate(rot, local)
