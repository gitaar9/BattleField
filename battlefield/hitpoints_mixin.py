import arcade


class HitPointsMixin:
    def __init__(self, hp):
        self.max_hp = 0
        self.hp = 0
        self.set_max_hp(hp)
        self.hit_cooldown_time = 4
        self.hit_cooldown = self.hit_cooldown_time

    def set_max_hp(self, hp, heal_to_full=True):
        self.max_hp = hp
        if heal_to_full:
            self.hp = hp

    def hit(self, damage):
        self.hp -= damage
        self.hit_cooldown += self.hit_cooldown_time

    def is_dead(self):
        return self.hp <= 0

    def draw_hp_bar(self, center_x, center_y, hp_bar_width, hp_bar_height=3):
        # HP Bar Background (Max HP) in red
        arcade.draw_rectangle_filled(
            center_x=center_x,
            center_y=center_y,
            # 5 pixels above the character
            width=hp_bar_width,
            height=hp_bar_height,
            color=arcade.color.RED
        )

        # Current HP in green
        current_hp_width = hp_bar_width * (self.hp / self.max_hp)
        arcade.draw_rectangle_filled(
            center_x=center_x - (hp_bar_width - current_hp_width) / 2,
            center_y=center_y,
            width=current_hp_width,
            height=hp_bar_height,
            color=arcade.color.GREEN
        )

    def update(self, *args, **kwargs):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1