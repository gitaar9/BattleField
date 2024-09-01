from a_star import closest_open_tile_to
from animation import Animation
from ai_character import AICharacter
from game_constants import STANDARD_FRAME_TIME, GRID_COLUMNS, GRID_ROWS


class AIArcher(AICharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attack_range = 8

        self.animations = {
            'facing_left': Animation("resources/ai_archer/archer_walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/ai_archer/archer_walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/ai_archer/archer_attack_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/ai_archer/archer_attack_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=9),
        }

    def find_goal_location(self, game_state):
        walkable_tiles = game_state.walkable_tiles

        # Immediate left and right locations
        open_places = []
        directions = [(-distance, 0) for distance in range(self.attack_range)] + [(distance, 0) for distance in range(self.attack_range)]
        for dx, dy in directions:
            x = game_state.player_character.grid_x + dx
            y = game_state.player_character.grid_y + dy
            if x == self.grid_x and y == self.grid_y:
                return None
            if 0 <= x < GRID_COLUMNS and 0 <= y < GRID_ROWS and walkable_tiles[y, x]:
                open_places.append((x, y))

        if open_places:  # Choose closest open place
            if (self.grid_x, self.grid_y) in open_places:
                return None
            return sorted(open_places, key=lambda t: abs(self.grid_x - t[0]) + (self.grid_y - t[1]))[0]

        return closest_open_tile_to(walkable_tiles, game_state.player_character.grid_x, game_state.player_character.grid_y)

    def is_facing_enemy(self, game_state):
        if self.grid_y == game_state.player_character.grid_y:
            if self.facing_left:
                return self.grid_x - self.attack_range < game_state.player_character.grid_x
            else:
                return self.grid_x + self.attack_range > game_state.player_character.grid_x
        else:
            return False