from parser import *
from utils import *


def agent(obs, config):

    print(obs)

    my_id = obs["player"]

    planets = parse_observation(obs)

    my_planets = get_my_planets(planets, my_id)

    enemy_planets = get_enemy_planets(planets, my_id)

    print("MY PLANETS")
    print(my_planets)

    print("TARGETS")
    print(enemy_planets)

    return None