import time

from animation import Animation
from game_constants import STANDARD_FRAME_TIME, MOVEMENT_DELAY
from walking_fighting_character import WalkingFightingCharacter
from weapon import Weapon


class PlayerCharacter(WalkingFightingCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weapon = Weapon(15, STANDARD_FRAME_TIME / 2, MOVEMENT_DELAY)

        self.animations.update({
            'facing_left': Animation("resources/main_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/main_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/main_character/attacks_left.png", 48, 48, 8, 16, frame_duration=self.weapon.frame_time, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/main_character/attack_right.png", 48, 48, 8, 16, frame_duration=self.weapon.frame_time, scale=1.0, loop=False, margin_x=9),
        })

    def handle_player_input(self, game_state, keys_pressed):
        if keys_pressed['space'] and (time.time() - self.last_move_time >= self.move_delay):
            self.fight()

        dx = keys_pressed['right'] - keys_pressed['left']
        dy = keys_pressed['up'] - keys_pressed['down']
        if (dx != 0 or dy != 0) and (time.time() - self.last_move_time >= self.move_delay):
            self.move(dx, dy, game_state.walkable_tiles)
