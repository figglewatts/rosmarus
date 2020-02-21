from __future__ import annotations
from collections import namedtuple
from typing import Callable

_resource_handlers = {}
_resource_cache = {}

resource = namedtuple("resource", ["loaded", "lifespan"])


def register_type_handler(resource_type: str,
                          loader: Callable[[str], object]) -> None:
    if resource_type in _resource_handlers:
        raise ValueError(
            f"Resource type handler '{resource_type}' already exists!")

    _resource_handlers[resource_type] = loader


def clear_lifespan(lifespan: str) -> None:
    if lifespan == "":
        raise ValueError("Unable to delete default resource lifespan")

    for k, r in _resource_cache.items():
        if r.lifespan == lifespan:
            del _resource_cache[k]


def load(resource_type: str, path: str, lifespan: str = "") -> object:
    if resource_type not in _resource_handlers:
        raise ValueError(
            f"No resource handler found for type '{resource_type}'")

    cached_resource = _check_cache(path)
    if cached_resource is not None:
        return cached_resource.value

    loaded_resource = _resource_handlers[resource_type](path)
    _resource_cache[path] = resource(loaded=loaded_resource, lifespan=lifespan)
    return loaded_resource


def _check_cache(path: str) -> resource:
    return _resource_cache.get(path, None)