import time
from pathlib import Path
from typing import List, Union

import arcade
from arcade import Texture


class Animation:
    def __init__(self, file_path: Union[Path, List[Texture]], frame_width, frame_height, columns, frame_count, frame_duration=0.05, scale=1.0, loop=True, margin_x=0):
        if isinstance(file_path, list):
            self.texture_list = file_path
        else:
            self.texture_list = arcade.load_spritesheet(file_path, frame_width, frame_height, columns, frame_count)

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.margin_x = margin_x
        self.frame_count = frame_count
        self.current_frame = 0
        self.scale = scale
        self.loop = loop
        self.playing = loop
        self.frame_duration = frame_duration  # Time in seconds for each frame
        self.last_update_time = time.time()
        self.animation_parts = 2

    def update(self):
        if not self.playing:
            return

        if time.time() - self.last_update_time > self.frame_duration:
            if self.loop:
                self.current_frame = (self.current_frame + 1) % self.frame_count
            else:
                self.current_frame = min(self.current_frame + 1, self.frame_count - 1)
                if self.current_frame == (self.frame_count // self.animation_parts) - 1:
                    self.playing = False
            self.last_update_time = time.time()

    def draw(self, center_x, center_y, perspective_factor=1):
        sprite = self.texture_list[self.current_frame]
        arcade.draw_texture_rectangle(center_x + self.margin_x * self.scale, center_y, sprite.width * self.scale, sprite.height * self.scale, sprite)

    def reset(self):
        if self.current_frame == self.frame_count - 1:
            self.current_frame = 0
        self.playing = True

    def get_animation_phase(self):
        return self.current_frame // (self.frame_count // self.animation_parts)

    def set_animation_phase(self, animation_phase):
        if animation_phase >= self.animation_parts:
            raise ValueError('Animation phase out of range')
        self.current_frame = (self.frame_count // self.animation_parts) * (animation_phase + 1) - 1

    def is_in_hit_frame(self):
        return (self.current_frame % (self.frame_count // self.animation_parts)) == 4
