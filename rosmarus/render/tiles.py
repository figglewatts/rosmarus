from __future__ import annotations
from typing import List, Tuple

import glm
from munch import Munch

from .sprite import Sprite
from .spritesheet import SpriteSheet
from .spritebatch import SpriteBatch


class Tile:
    def __init__(self, tile_id: int = 0, sheet_id: int = 0) -> None:
        self.id = tile_id
        self.sheet_id = sheet_id
        self.user_data = Munch()


class TileLayer:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = [[Tile() for x in range(width)]
                                        for y in range(height)]

    def __getitem__(self, pos: Tuple[int, int]) -> Tile:
        x, y = pos
        return self.tiles[y][x]

    def __setitem__(self, pos: Tuple[int, int], data: Tile) -> None:
        x, y = pos
        self.tiles[y][x] = data

    def fill(self, tile: Tile) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self[x, y] = tile


class TileMap:
    def __init__(self,
                 tile_sheet: SpriteSheet,
                 width: int,
                 height: int,
                 render_tiles_x: int,
                 render_tiles_y: int,
                 position: glm.vec2 = glm.vec2()) -> None:
        self.sheets: List[SpriteSheet] = []
        self.add_sheet(tile_sheet)
        self.width = width
        self.height = height
        self.layers: List[TileLayer] = []
        self.add_layer()
        self.render_tiles_x = render_tiles_x
        self.render_tiles_y = render_tiles_y
        self.position = position

    def __getitem__(self, pos: Tuple[int, int]) -> Tile:
        """Shortcut for getting from the base layer."""
        x, y = pos
        return self.layers[0][x, y]

    def __setitem__(self, pos: Tuple[int, int], data: Tile) -> None:
        """Shortcut for setting tiles in the base layer."""
        x, y = pos
        self.layers[0][x, y] = data

    def fill(self, tile: Tile) -> None:
        """Shortcut for filling the base layer."""
        self.layers[0].fill(tile)

    def set_position(self, x: int, y: int) -> None:
        self.position = glm.vec2(x, y)

    def add_layer(self) -> TileLayer:
        layer = TileLayer(self.width, self.height)
        self.layers.append(layer)
        return layer

    def get_layer(self, index: int) -> TileLayer:
        return self.layers[index]

    def add_sheet(self, sheet: SpriteSheet) -> None:
        self.sheets.append(sheet)

    def get_sprite(self, tile: Tile, x: int, y: int) -> Sprite:
        sheet = self.sheets[tile.sheet_id]
        x_pos = self.position.x + x * sheet.sprite_width
        y_pos = self.position.y + y * sheet.sprite_height
        return sheet.get_sprite(tile.id - 1, x_pos=x_pos, y_pos=y_pos)

    def draw(self, batch: SpriteBatch) -> None:
        cam_pos = batch.camera.transform.get_position()
        tile_w = self.sheets[0].sprite_width
        tile_h = self.sheets[0].sprite_height
        first_square = glm.vec2(cam_pos.x / tile_w, cam_pos.y / tile_h)

        for layer in self.layers:
            for y in range(0, self.render_tiles_y):
                for x in range(0, self.render_tiles_x):
                    tile_x = int(first_square.x) + x
                    tile_y = int(first_square.y) - y

                    if tile_x >= self.width or tile_y >= self.height \
                        or tile_x < 0 or tile_y < 0:
                        continue

                    tile = layer[tile_x, tile_y]
                    if tile.id == 0:
                        continue

                    self.get_sprite(tile, tile_x, tile_y).draw(batch)
