import random

from a_star import next_step_direction, closest_open_tile_to
from animation import Animation
from game_constants import STANDARD_FRAME_TIME, GRID_COLUMNS, GRID_ROWS
from walking_fighting_character import WalkingFightingCharacter


class AICharacter(WalkingFightingCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.animations = {
            'facing_left': Animation("resources/farmer_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/farmer_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/ai_character/attacks_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/ai_character/attack_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=9),
        }

    def find_goal_location(self, game_state):
        walkable_tiles = game_state.walkable_tiles

        # Immediate left and right locations
        open_places = []
        directions = [(-1, 0), (1, 0)]
        for dx, dy in directions:
            x = game_state.player_character.grid_x + dx
            y = game_state.player_character.grid_y + dy
            if x == self.grid_x and y == self.grid_y:
                return None
            if 0 <= x < GRID_COLUMNS and 0 <= y < GRID_ROWS and walkable_tiles[y, x]:
                open_places.append((x, y))

        if open_places:  # Choose closest open place
            return sorted(open_places, key=lambda t: abs(self.grid_x - t[0]) + (self.grid_y - t[1]))[0]

        return closest_open_tile_to(walkable_tiles, game_state.player_character.grid_x, game_state.player_character.grid_y)

    def is_facing_enemy(self, game_state):
        if self.grid_y == game_state.player_character.grid_y:
            if self.facing_left:
                return self.grid_x - 1 == game_state.player_character.grid_x
            else:
                return self.grid_x + 1 == game_state.player_character.grid_x
        else:
            return False

    def handle_ai_planning(self, game_state, keys_pressed, walkable_tiles):
        # Sometimes just do nothing
        if not self.move_delay_active and random.random() < 0.05:
            self.set_last_move_time()

        # Attack if an enemy is right in front of you
        if not self.move_delay_active and random.random() < 0.06 and self.is_facing_enemy(game_state):
            self.fight()

        # Move towards and enemy
        if not self.move_delay_active:
            goal_location = self.find_goal_location(game_state)
            if goal_location is not None:
                dx, dy = next_step_direction(tuple(reversed(goal_location)), walkable_tiles, (self.grid_y, self.grid_x))
                if dx != 0 or dy != 0:
                    self.move(dx, dy, walkable_tiles)
            else:
                # This is such that the character faces to player_character
                self.move(max(-1, min(1, game_state.player_character.grid_x - self.grid_x)), 0, walkable_tiles)

