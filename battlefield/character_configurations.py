import random

from ai_archer import AIArcher
from ai_character import AICharacter, AIKnight
from game_constants import CELL_SIZE, MOVEMENT_DELAY


def old_default_characters():
    return [
        AIArcher(
            position_x=20,
            position_y=2,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AIArcher(
            position_x=20,
            position_y=5,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AIArcher(
            position_x=20,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AIArcher(
            position_x=22,
            position_y=1,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AIArcher(
            position_x=22,
            position_y=4,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AIArcher(
            position_x=22,
            position_y=7,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=2,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=5,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=1,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=4,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=7,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
    ]


def default_characters():
    return [
        AICharacter(
            position_x=18,
            position_y=2,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=5,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=18,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=20,
            position_y=2,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=20,
            position_y=5,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=20,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AICharacter(
            position_x=5,
            position_y=1,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AICharacter(
            position_x=5,
            position_y=4,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AICharacter(
            position_x=5,
            position_y=7,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AICharacter(
            position_x=5,
            position_y=6,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AICharacter(
            position_x=5,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=0
        ),
        AIArcher(
            position_x=18,
            position_y=7,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
        AIKnight(
            position_x=21,
            position_y=8,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
    ]


def one_enemy_archer():
    return [
        AIArcher(
            position_x=18,
            position_y=7,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=1
        ),
    ]


def get_random_ai_character(x, y, team):
    random_number = random.random()
    number_classes = 3
    if random_number < 1 / number_classes:
        return AICharacter(
            position_x=x,
            position_y=y,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=team
        )
    if random_number < 1 / number_classes * 2:
        return AIKnight(
            position_x=x,
            position_y=y,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=team
        )
    else:
        return AIArcher(
            position_x=x,
            position_y=y,
            cell_size=CELL_SIZE,
            move_delay=MOVEMENT_DELAY,
            team=team
        )


def random_10_vs_10():
    ai_characters = []
    friendly_positions = [
        (5, 3), (6, 3),
        (5, 4), (6, 4),
        (5, 5), (6, 5),
        (5, 6), (6, 6),
        (5, 7), (6, 7),
    ]
    enemy_positions = [
        (18, 3), (19, 3),
        (18, 4), (19, 4),
        (18, 5), (19, 5),
        (18, 6), (19, 6),
        (18, 7), (19, 7),
    ]
    for x, y in friendly_positions:
        ai_characters.append(
            get_random_ai_character(x, y, 0)
        )
    for x, y in enemy_positions:
        ai_characters.append(
            get_random_ai_character(x, y, 1)
        )
    return ai_characters


def archer_10_vs_10():
    ai_characters = []
    friendly_positions = [
        (5, 3), (6, 3),
        (5, 4), (6, 4),
        (5, 5), (6, 5),
        (5, 6), (6, 6),
        (5, 7), (6, 7),
    ]
    enemy_positions = [
        (18, 3), (19, 3),
        (18, 4), (19, 4),
        (18, 5), (19, 5),
        (18, 6), (19, 6),
        (18, 7), (19, 7),
    ]
    for x, y in friendly_positions:
        ai_characters.append(
            AIArcher(
                position_x=x,
                position_y=y,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=0
            )
        )
    for x, y in enemy_positions:
        ai_characters.append(
            AIArcher(
                position_x=x,
                position_y=y,
                cell_size=CELL_SIZE,
                move_delay=MOVEMENT_DELAY,
                team=1
            )
        )
    return ai_characters