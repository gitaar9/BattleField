import math

import arcade
from arcade import View, Window, Color, Sprite


class Town(arcade.Sprite):
    def __init__(self, x: float, y: float, radius: float, name: str, game_view):
        """
        Initialize a town represented as a circle.

        Args:
            x (float): X-coordinate of the town center.
            y (float): Y-coordinate of the town center.
            radius (float): Radius of the town circle.
            name (str): The name of the town.
        """
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.color = arcade.color.RED
        self.name = name
        self.town_view = TownView(self, game_view)

    def draw(self):
        """ Draw the town as a red circle and display the name below it. """
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
        arcade.draw_text(self.name, self.center_x, self.center_y,
                         arcade.color.BLACK, 12, width=self.radius, align="center",
                         anchor_x="center", anchor_y="center")


class MainCharacter(Sprite):
    def __init__(self, color: Color, size: int, speed: float):
        """
        Initialize a character sprite that moves towards a target location.

        Args:
            color (Color): The color of the sprite.
            size (int): The size of the sprite in pixels.
            speed (float): The movement speed of the sprite (higher is faster).
        """
        super().__init__()
        self.texture = arcade.make_soft_square_texture(size=size, color=color)
        self.center_x = 400
        self.center_y = 300
        self.target_x = 400
        self.target_y = 300
        self.speed = speed  # Higher values mean faster movement

    def update_target(self, x: float, y: float):
        """
        Update the target location where the sprite should move.

        Args:
            x (float): The target x-coordinate.
            y (float): The target y-coordinate.
        """
        self.target_x = x
        self.target_y = y

    def update(self):
        """
        Move the sprite towards the target location based on its speed.
        """
        self.center_x += (self.target_x - self.center_x) / self.speed
        self.center_y += (self.target_y - self.center_y) / self.speed

    def put_outside_of_town(self, town: Town):
        # self.center_x = town.center_x + town.radius + 5
        self.center_y = town.center_y - (town.radius * 2)
        self.stop()

    def stop(self):
        self.target_x = self.center_x
        self.target_y = self.center_y

    def stands_still(self):
        return (abs(self.target_x - self.center_x) + abs(self.target_y - self.center_y)) < 10


class StartView(View):
    def __init__(self):
        """
        Initialize the start view which contains a start button.
        """
        super().__init__()
        self.game_view = GameView(self)

    def on_show(self):
        """
        Set the background color when the view is shown.
        """
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        """
        Render the start screen with a text prompt.
        """
        arcade.start_render()
        arcade.draw_text("Click to start", 400, 300, arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x: float, _y: float, _button: int, _modifiers: int):
        """
        Handle mouse press events to start the game.

        Args:
            _x (float): X-coordinate of the mouse click.
            _y (float): Y-coordinate of the mouse click.
            _button (int): Mouse button pressed.
            _modifiers (int): Keyboard modifiers.
        """
        self.window.show_view(self.game_view)

class GameView(arcade.View):
    def __init__(self, start_view: StartView):
        super().__init__()
        self.start_view = start_view
        self.main_character = MainCharacter(arcade.color.BLUE, 50, 20)  # Speed is 20
        self.towns = [
            Town(500, 300, 30, "Old Town", self),
            Town(100, 100, 30, "North Village", self)
        ]

    def on_show(self):
        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_draw(self):
        arcade.start_render()
        for town in self.towns:
            town.draw()
        self.main_character.draw()

    def on_update(self, delta_time: float):
        self.main_character.update()
        # Manually check for collision
        if self.main_character.stands_still():
            for town in self.towns:
                if self.check_collision_with_town(town):
                    self.window.show_view(town.town_view)
                    break

    def check_collision_with_town(self, town: Town):
        distance = math.sqrt((self.main_character.center_x - town.center_x) ** 2 +
                             (self.main_character.center_y - town.center_y) ** 2)
        return distance < (town.radius + 25)


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Update the target position of the main character on mouse click.

        Args:
            x (float): X-coordinate of the mouse click.
            y (float): Y-coordinate of the mouse click.
            button (int): Mouse button pressed.
            modifiers (int): Keyboard modifiers.
        """
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.main_character.update_target(x, y)

    def on_key_press(self, key: int, modifiers: int):
        """
        Handle key press events to navigate back to the start view.

        Args:
            key (int): The key pressed.
            modifiers (int): Keyboard modifiers.
        """
        if key == arcade.key.ESCAPE:  # Check if ESCAPE key is pressed
            self.window.show_view(self.start_view)  # Switch to the start screen


class TownView(arcade.View):
    def __init__(self, town: Town, game_view: GameView):
        """
        Initialize the town view.

        Args:
            game_view (GameView): The game view to return to.
        """
        super().__init__()
        self.game_view = game_view
        self.town = town

    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(f"Welcome to {self.town.name}", 400, 300, arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("Click to return", 400, 250, arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x: float, _y: float, _button: int, _modifiers: int):
        # Adjust the character position slightly outside the town radius
        self.game_view.main_character.put_outside_of_town(self.town)
        self.window.show_view(self.game_view)


def main():
    """
    Main function to create the window and start the Arcade application.
    """
    window = Window(800, 600, "Sprite Move Game")
    window.set_update_rate(1/60)  # Set the update interval to 1/60th of a second
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
