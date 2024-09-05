from collections import deque

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from game_constants import GRID_COLUMNS, GRID_ROWS


def next_step_direction(goal, walkable_tiles, current):
    grid = Grid(matrix=walkable_tiles.astype(int))

    start = grid.node(current[1], current[0])  # x, y reversed in the grid node
    end = grid.node(goal[1], goal[0])  # x, y reversed in the grid node

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    if len(path) > 1:
        # Path[0] is the current position, path[1] is the next step
        next_x, next_y = path[1]
        dx = next_x - current[1]
        dy = next_y - current[0]
    else:
        dx, dy = 0, 0  # No movement if no path or already at the goal

    # Ensure dx, dy are -1, 0, or 1
    dx = max(-1, min(1, dx))
    dy = max(-1, min(1, dy))

    return dx, dy


def closest_open_tile_to(walkable_tiles, goal_x, goal_y):
    # BFS for closest walkable tile if immediate left/right is not available
    visited = set()
    queue = deque([(goal_x, goal_y)])
    visited.add((goal_x, goal_y))

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Only 4 directions, no diagonals
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS:
                if walkable_tiles[ny, nx] and (nx, ny) not in visited:
                    return nx, ny
                visited.add((nx, ny))
                queue.append((nx, ny))

    return None  # In case all fails (highly unlikely unless fully surrounded by unwalkable tiles)


