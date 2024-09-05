import arcade

from draw_utils import calculate_perspective_factor
from game_constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, GRID_ROWS, CELL_SIZE, GRID_COLUMNS, \
    BOTTOM_GRID_PAD, HORIZONTAL_PADDING
from game_state import GameState


class BattlefieldWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_update_rate(1/60)
        # Background texture
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.background_texture = arcade.load_texture("resources/backgrounds/background_image.webp")  # Load the background image

        # Player character and controls
        self.keys_pressed = {'left': 0, 'right': 0, 'up': 0, 'down': 0, 'space': 0}

        self.game_state = GameState()

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw the background image, scaled to fit the screen
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_texture)

        # Draw the grid with perspective
        draw_grid = True
        empty_tiles = self.game_state.walkable_tiles
        if draw_grid:
            for y in range(GRID_ROWS):
                perspective_factor = calculate_perspective_factor(y)
                cell_width = CELL_SIZE * perspective_factor
                cell_height = CELL_SIZE * perspective_factor
                for x in range(GRID_COLUMNS):
                    screen_x = x * cell_width + (SCREEN_WIDTH / 2) - (GRID_COLUMNS * cell_width / 2)
                    screen_y = y * cell_height + BOTTOM_GRID_PAD + HORIZONTAL_PADDING * y
                    alpha = 40
                    color = (0, 0, 0, alpha) if empty_tiles[y, x] else (225, 0, 0, alpha + 40)
                    arcade.draw_rectangle_outline(screen_x + cell_width / 2, screen_y + cell_height / 2,
                                                  cell_width, cell_height, color, 3)

        for drawable in sorted(self.game_state.drawables, key=lambda t: (t.screen_y, -t.screen_x), reverse=True):
            drawable.draw()  # Draw the tree or player

    def on_update(self, delta_time):
        """ Update game logic based on key states. """
        self.game_state.update_game_grid()

        self.game_state.player_character.update(delta_time, self.game_state, self.keys_pressed)

        for ai_character in self.game_state.ai_characters:
            ai_character.update(delta_time, self.game_state, self.keys_pressed)

    def on_key_press(self, key, modifiers):
        """ Handle key presses for player movement. """
        if key in {arcade.key.A, arcade.key.LEFT}:
            self.keys_pressed['left'] = 1
        elif key in {arcade.key.D, arcade.key.RIGHT}:
            self.keys_pressed['right'] = 1
        elif key in {arcade.key.W, arcade.key.UP}:
            self.keys_pressed['up'] = 1
        elif key in {arcade.key.S, arcade.key.DOWN}:
            self.keys_pressed['down'] = 1
        elif key in {arcade.key.SPACE}:
            self.keys_pressed['space'] = 1

    def on_key_release(self, key, modifiers):
        """ Handle key releases. """
        if key in {arcade.key.A, arcade.key.LEFT}:
            self.keys_pressed['left'] = 0
        elif key in {arcade.key.D, arcade.key.RIGHT}:
            self.keys_pressed['right'] = 0
        elif key in {arcade.key.W, arcade.key.UP}:
            self.keys_pressed['up'] = 0
        elif key in {arcade.key.S, arcade.key.DOWN}:
            self.keys_pressed['down'] = 0
        elif key in {arcade.key.SPACE}:
            self.keys_pressed['space'] = 0
