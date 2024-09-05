import random

from a_star import next_step_direction, closest_open_tile_to
from animation import Animation
from game_constants import STANDARD_FRAME_TIME, GRID_COLUMNS, GRID_ROWS, MOVEMENT_DELAY
from walking_fighting_character import WalkingFightingCharacter


class AICharacter(WalkingFightingCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.target = None

        self.animations.update({
            'facing_left': Animation("resources/farmer_character/walk_left.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=-9),
            'facing_right': Animation("resources/farmer_character/walk_right.png", 48, 48, 8, 8, frame_duration=STANDARD_FRAME_TIME, scale=1.0, loop=False, margin_x=9),
            'fighting_left': Animation("resources/ai_character/attacks_left.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=-9),
            'fighting_right': Animation("resources/ai_character/attack_right.png", 48, 48, 8, 16, frame_duration=STANDARD_FRAME_TIME / 2, scale=1.0, loop=False, margin_x=9),
        })

    def find_goal_location(self, game_state):
        walkable_tiles = game_state.walkable_tiles

        # Immediate left and right locations
        open_places = []
        directions = [(-1, 0), (1, 0)]
        for dx, dy in directions:
            x = self.target.grid_x + dx
            y = self.target.grid_y + dy
            if x == self.grid_x and y == self.grid_y:
                return None
            if 0 <= x < GRID_COLUMNS and 0 <= y < GRID_ROWS and walkable_tiles[y, x]:
                open_places.append((x, y))

        if open_places:  # Choose closest open place
            return sorted(open_places, key=lambda t: abs(self.grid_x - t[0]) + (self.grid_y - t[1]))[0]

        return closest_open_tile_to(walkable_tiles, self.target.grid_x, self.target.grid_y)

    def is_facing_enemy(self, game_state):
        if self.grid_y == self.target.grid_y:
            if self.facing_left:
                return self.grid_x - 1 == self.target.grid_x
            else:
                return self.grid_x + 1 == self.target.grid_x
        else:
            return False

    def bfs_for_target(self, start, game_state):
        from collections import deque

        queue = deque([start])
        visited = {start}
        directions = [(-1 if self.facing_left else 1, 0), (0, -1), (0, 1)]  # Moving left, right, up, down

        while queue:
            current_x, current_y = queue.popleft()

            # Check if the current position has an enemy
            current_tile = game_state.game_grid[current_y][current_x]
            from walking_fighting_character import WalkingFightingCharacter
            if current_tile is not None and isinstance(current_tile, WalkingFightingCharacter):
                if current_tile.team != self.team and not current_tile.is_dead():
                    return current_tile

            # Explore neighbors
            for dx, dy in directions:
                neighbor_x, neighbor_y = current_x + dx, current_y + dy
                if 0 <= neighbor_x < GRID_COLUMNS and 0 <= neighbor_y < GRID_ROWS:
                    if (neighbor_x, neighbor_y) not in visited:
                        visited.add((neighbor_x, neighbor_y))
                        queue.append((neighbor_x, neighbor_y))
        return None
    def find_target(self, game_state, keys_pressed):
        self.target = self.bfs_for_target((self.grid_x, self.grid_y), game_state)

    def switch_target_to_closeby_enemy(self, game_state):
        dx = random.randint(-1, 1)
        neighbouring_tile = game_state.game_grid[self.grid_y][self.grid_x + dx]
        if isinstance(neighbouring_tile, WalkingFightingCharacter) and neighbouring_tile.team != self.team and not neighbouring_tile.is_dead():
            self.target = neighbouring_tile
            return


    def handle_ai_planning(self, game_state, keys_pressed):
        if self.target is None or self.target.is_dead():
            self.find_target(game_state, keys_pressed)

        if self.target is None:
            if not self.move_delay_active:
                self.facing_left = not self.facing_left
                self.set_last_move_time(MOVEMENT_DELAY)
            return

        if not self.move_delay_active and not self.is_facing_enemy(game_state):
            self.switch_target_to_closeby_enemy(game_state)

        # Sometimes just do nothing
        if not self.move_delay_active and random.random() < 0.05:
            self.set_last_move_time(MOVEMENT_DELAY)

        # Attack if an enemy is right in front of you
        if not self.move_delay_active and random.random() < 0.06 and self.is_facing_enemy(game_state):
            self.fight()

        # Move towards and enemy
        if not self.move_delay_active and not self.is_facing_enemy(game_state):
            goal_location = self.find_goal_location(game_state)
            if goal_location is not None:
                walkable_tiles = game_state.walkable_tiles
                dx, dy = next_step_direction(tuple(reversed(goal_location)), walkable_tiles, (self.grid_y, self.grid_x))
                if dx != 0 or dy != 0:
                    self.move(dx, dy, walkable_tiles)
            else:
                # Face towards the player
                if self.target.grid_x - self.grid_x < 0:
                    self.facing_left = True
                if self.target.grid_x - self.grid_x > 0:
                    self.facing_left = False
