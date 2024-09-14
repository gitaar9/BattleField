import time

from animation import Animation
from game_constants import STANDARD_FRAME_TIME, MOVEMENT_DELAY
from piskel import Piskel
from walking_fighting_character import WalkingFightingCharacter
from weapon import Weapon


class ItemPiskels:
    def __init__(self, piskel_layers, walk_piskel, death_piskel, large_sword_attack_piskel=None, bow_attack_piskel=None, spear_attack_piskel=None):
        self.piskel_layers = piskel_layers
        self.walk_piskel = walk_piskel
        self.death_piskel = death_piskel
        self.large_sword_attack_piskel = large_sword_attack_piskel
        self.bow_attack_piskel = bow_attack_piskel
        self.spear_attack_piskel = spear_attack_piskel

class LegArmor:
    pass


class PlateLegs(LegArmor):
    def __init__(self):
        self.piskels = ItemPiskels(
            piskel_layers=['Left leg', 'Right leg'],
            walk_piskel=Piskel('./piksel_files/main_character/walk.piskel'),
            death_piskel=Piskel('./piksel_files/main_character/death.piskel'),
            large_sword_attack_piskel=Piskel('./piksel_files/main_character/large_sword_attack.piskel')
        )
        self.piskels = ItemPiskels(
            piskel_layers=['Left leg', 'Right leg'],
            walk_piskel=Piskel('./piksel_files/farmer_character/walk.piskel'),
            death_piskel=Piskel('./piksel_files/farmer_character/death.piskel'),
            large_sword_attack_piskel=Piskel('./piksel_files/farmer_character/spear_attack.piskel')
        )


class ChestArmor:
    pass


class PlateChest(ChestArmor):
    def __init__(self):
        self.piskels = ItemPiskels(
            piskel_layers=['Torso', 'Head', 'Left arm', 'Right arm'],
            walk_piskel=Piskel('./piksel_files/main_character/walk.piskel'),
            death_piskel=Piskel('./piksel_files/main_character/death.piskel'),
            large_sword_attack_piskel=Piskel('./piksel_files/main_character/large_sword_attack.piskel')
        )


class PlayerCharacter(WalkingFightingCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weapon = Weapon(15, STANDARD_FRAME_TIME / 2, MOVEMENT_DELAY)
        self.leg_armor = PlateLegs()
        self.chest_armor = PlateChest()

        self.animations.update({
            'facing_left': Animation("resources/main_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/main_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': self.fighting_animation(left=True),
            'fighting_right': self.fighting_animation(left=False),
            'death_left': Animation("resources/main_character/death_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'death_right': Animation("resources/main_character/death_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
        })

    def fighting_animation(self, left=True):
        piskels_with_layers = [
            (self.chest_armor.piskels.large_sword_attack_piskel, self.chest_armor.piskels.piskel_layers),
            (self.leg_armor.piskels.large_sword_attack_piskel, self.leg_armor.piskels.piskel_layers),
            (self.weapon.piskels.large_sword_attack_piskel, self.weapon.piskels.piskel_layers),
        ]
        fighting_piskel = Piskel.combine_piskels(piskels_with_layers)
        if not left:
            fighting_piskel.fliplr()
        return fighting_piskel.get_animation(self.weapon.frame_time)

    def handle_player_input(self, game_state, keys_pressed):
        if keys_pressed['space'] and (time.time() - self.last_move_time >= self.move_delay):
            self.fight()

        dx = keys_pressed['right'] - keys_pressed['left']
        dy = keys_pressed['up'] - keys_pressed['down']
        if (dx != 0 or dy != 0) and (time.time() - self.last_move_time >= self.move_delay):
            self.move(dx, dy, game_state.walkable_tiles)
