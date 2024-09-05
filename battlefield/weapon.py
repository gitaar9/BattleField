

class Weapon:
    def __init__(self, damage, frame_time, move_delay_time):
        self.damage = damage
        self.frame_time = frame_time
        self.move_delay_time = move_delay_time
        self.hit_cooldown_time = 5
        self.hit_cooldown = self.hit_cooldown_time

    def update(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def reset_hit_cooldown(self):
        self.hit_cooldown = self.hit_cooldown_time
