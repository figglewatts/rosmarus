from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from methodtools import lru_cache
import glm

from .graphics.camera import Camera
from .graphics.window import Window


class Scene(ABC):
    def __init__(self,
                 window: Window,
                 name: str,
                 order: int = 0,
                 active: bool = False) -> None:
        self.name = name
        self.active = active
        self.order = order
        self.window = window

    def _set_active(self, state: bool) -> None:
        self.active = state
        if state:
            self.on_active()

    @abstractmethod
    def init(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def update(self, delta_time: float, *args, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def render(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class SceneManager:
    def __init__(self) -> None:
        self.scenes = {}

    def add_scene(self, scene: Scene) -> Scene:
        if scene.name in self.scenes:
            raise ValueError(
                f"Scene with name '{scene.name}' already managed!")
        self.scenes[scene.name] = scene
        scene.init()
        self._active_scenes.cache_clear()

    def deactivate_all(self) -> None:
        self._active_scenes.cache_clear()
        for scene in self.scenes.values():
            scene._set_active(False)

    def set_scene_active(self, name: str, state: bool) -> None:
        self._active_scenes.cache_clear()
        self.scenes[name]._set_active(state)

    def init(self, *args, **kwargs) -> None:
        for scene in self.scenes.values():
            scene.init(*args, **kwargs)

    def update(self, delta_time: float, *args, **kwargs) -> None:
        for scene in self._active_scenes():
            scene.update(delta_time, *args, **kwargs)

    def render(self, *args, **kwargs) -> None:
        for scene in self._active_scenes():
            scene.render(*args, **kwargs)

    @lru_cache(maxsize=1)
    def _active_scenes(self) -> List[Scene]:
        return sorted(
            (scene for scene in self.scenes.values() if scene.active),
            key=lambda scene: scene.order)
