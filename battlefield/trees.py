from game_constants import CELL_SIZE
from stationary_sprite import StationarySprite


class Tree1(StationarySprite):
    def __init__(self, position_x, position_y):
        super().__init__(
            position_x=position_x,
            position_y=position_y,
            cell_size=CELL_SIZE,
            image_file="resources/props/cutout_tree1.webp",
            bottom_padding=2,
            cell_size_factor=2,
            random_horizontal_flip=True
        )


class Tree2(StationarySprite):
    def __init__(self, position_x, position_y):
        super().__init__(
            position_x=position_x,
            position_y=position_y,
            cell_size=CELL_SIZE,
            image_file="resources/props/cutout_tree2.webp",
            bottom_padding=3,
            cell_size_factor=2,
            random_horizontal_flip=True
        )
