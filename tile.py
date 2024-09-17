
# tile.py
import pygame

TILE_SIZE = 60

class Tile:
    def __init__(self, name, position, layer, state):
        self.name = name
        self.image = pygame.image.load(name)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))  # 确保图片被缩放为 TILE_SIZE
        self.position = position
        self.rect = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE)
        self.layer = layer
        self.state = state  # 0: top layer, 1: non-top layer
        self.id = id(self)  # Unique identifier for this tile


