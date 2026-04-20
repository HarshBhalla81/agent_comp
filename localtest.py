"""
Local Test Runner
=================
Simulates a game between your agent and a simple opponent.
Run this to test your agent BEFORE submitting to Kaggle.

Usage:
    python test_locally.py
    python test_locally.py --turns 100
    python test_locally.py --verbose
"""

import math
import random
import argparse
import sys
import os

# Add agent folder to path so we can import it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agent"))
from agent.main import agent


# ─────────────────────────────────────────────
#  SIMPLE GAME SIMULATOR
# ─────────────────────────────────────────────

class Planet:
    def __init__(self, pid, owner, x, y, ships, production):
        self.id         = pid
        self.owner      = owner
        self.x          = x
        self.y          = y
        self.radius     = 1 + math.log(production)
        self.ships      = ships
        self.production = production

    def to_list(self):
        return [self.id, self.owner, self.x, self.y,
                self.radius, round(self.ships), self.production]


class Fleet:
    def __init__(self, fid, owner, x, y, angle, from_id, ships):
        self.id       = fid
        self.owner    = owner
        self.x        = x
        self.y        = y
        self.angle    = angle
        self.from_id  = from_id
        self.ships    = ships
        self.alive    = True
        speed_factor  = (math.log(max(ships, 2)) / math.log(1000)) ** 1.5
        self.speed    = 1.0 + 5.0 * speed_factor

    def to_list(self):
        return [self.id, self.owner, round(self.x, 2), round(self.y, 2),
                self.angle, self.from_id, self.ships]

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def random_agent(obs):
    """A simple random opponent for testing."""
    me      = obs.get("player", 1)
    planets = obs.get("planets", [])
    my_p    = [p for p in planets if p[1] == me and p[5] > 10]
    others  = [p for p in planets if p[1] != me]
    if not my_p or not others:
        return []
    src = random.choice(my_p)
    tgt = random.choice(others)
    angle = math.atan2(tgt[3] - src[3], tgt[2] - src[2])
    send  = src[5] // 3
    if send < 1:
        return []
    return [[src[0], angle, send]]


def simulate(turns=200, verbose=False, seed=42):
    random.seed(seed)
    SUN_X, SUN_Y, SUN_R = 50, 50, 10

    # Create symmetric map
    planets = [
        Planet(0, 0,  15, 85, 10, 3),   # player 0 home
        Planet(1, 1,  85, 15, 10, 3),   # player 1 home
        Planet(2, -1, 30, 50, 6,  2),   # neutral mid-left
        Planet(3, -1, 70, 50, 6,  2),   # neutral mid-right
        Planet(4, -1, 50, 25, 4,  1),   # neutral top
        Planet(5, -1, 50, 75, 4,  1),   # neutral bottom
        Planet(6, -1, 20, 20, 5,  2),   # neutral corner
        Planet(7, -1, 80, 80, 5,  2),   # neutral corner
    ]

    fleets    = []
    fleet_ctr = [100]

    def make_obs(player_id):
        return {
            "player":  player_id,
            "planets": [p.to_list() for p in planets],
            "fleets":  [f.to_list() for f in fleets if f.alive],
        }

    def launch(moves, owner):
        for move in moves:
            if len(move) != 3:
                continue
            from_id, angle, num_ships = move
            src = next((p for p in planets if p.id == from_id and p.owner == owner), None)
            if src is None:
                continue
            num_ships = int(min(num_ships, src.ships - 1))
            if num_ships < 1:
                continue
            src.ships -= num_ships
            fleet_ctr[0] += 1
            fleets.append(Fleet(fleet_ctr[0], owner, src.x, src.y, angle, from_id, num_ships))

    def do_combat():
        for p in planets:
            arriving = [f for f in fleets if f.alive and dist(f, p) < p.radius + f.speed + 0.5]
            if not arriving:
                continue
            # Group by owner
            groups = {}
            for f in arriving:
                groups[f.owner] = groups.get(f.owner, 0) + f.ships
                f.alive = False
            if p.owner in groups:
                p.ships += groups.pop(p.owner)
            # Largest force vs second largest
            sorted_forces = sorted(groups.items(), key=lambda x: -x[1])
            if not sorted_forces:
                continue
            top_owner, top_ships = sorted_forces[0]
            if len(sorted_forces) > 1:
                top_ships -= sorted_forces[1][1]
            if top_ships <= 0:
                continue
            # Fight garrison
            if top_ships > p.ships:
                p.owner  = top_owner
                p.ships  = top_ships - p.ships
            else:
                p.ships -= top_ships

    def score(player_id):
        s = sum(p.ships for p in planets if p.owner == player_id)
        s += sum(f.ships for f in fleets if f.alive and f.owner == player_id)
        return int(s)

    # ── Main loop ──────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  ORBIT WARS LOCAL SIMULATION  ({turns} turns)")
    print(f"{'─'*50}")

    for turn in range(turns):
        # Production
        for p in planets:
            if p.owner >= 0:
                p.ships += p.production

        # Agents decide
        try:
            moves0 = agent(make_obs(0))
        except Exception as e:
            print(f"[Turn {turn}] YOUR AGENT CRASHED: {e}")
            moves0 = []
        moves1 = random_agent(make_obs(1))

        launch(moves0, 0)
        launch(moves1, 1)

        # Move fleets
        for f in fleets:
            if f.alive:
                f.move()
                # Out of bounds or sun collision
                if not (0 <= f.x <= 100 and 0 <= f.y <= 100):
                    f.alive = False
                if math.hypot(f.x - SUN_X, f.y - SUN_Y) < SUN_R:
                    f.alive = False

        do_combat()
        fleets[:] = [f for f in fleets if f.alive]

        # Periodic status
        if verbose or (turn + 1) % 50 == 0:
            s0 = score(0)
            s1 = score(1)
            p0 = len([p for p in planets if p.owner == 0])
            p1 = len([p for p in planets if p.owner == 1])
            bar_len = 30
            filled  = int(bar_len * s0 / max(s0 + s1, 1))
            bar     = "█" * filled + "░" * (bar_len - filled)
            print(f"  Turn {turn+1:>3} │ YOU [{bar}] ENEMY │ "
                  f"Ships: {s0:>4} vs {s1:>4} │ Planets: {p0} vs {p1}")

    # ── Final result ───────────────────────────
    s0, s1 = score(0), score(1)
    print(f"\n{'─'*50}")
    if s0 > s1:
        result = "YOU WIN"
        symbol = "+"
    elif s1 > s0:
        result = "YOU LOSE"
        symbol = "-"
    else:
        result = "DRAW"
        symbol = "="

    print(f"  RESULT: [{symbol}] {result}")
    print(f"  Final ships — You: {s0}   Enemy: {s1}")
    print(f"  Planets owned — You: {len([p for p in planets if p.owner==0])}   "
          f"Enemy: {len([p for p in planets if p.owner==1])}")
    print(f"{'─'*50}\n")
    return s0, s1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test your Orbit Wars agent locally")
    parser.add_argument("--turns",   type=int, default=200,  help="Number of turns to simulate")
    parser.add_argument("--verbose", action="store_true",    help="Print every turn")
    parser.add_argument("--games",   type=int, default=1,    help="Run multiple games with different seeds")
    args = parser.parse_args()

    wins = losses = draws = 0
    for g in range(args.games):
        s0, s1 = simulate(turns=args.turns, verbose=args.verbose, seed=g*7+42)
        if s0 > s1:   wins   += 1
        elif s1 > s0: losses += 1
        else:         draws  += 1

    if args.games > 1:
        print(f"SUMMARY over {args.games} games: "
              f"Wins={wins}  Losses={losses}  Draws={draws}  "
              f"WinRate={wins/args.games*100:.0f}%\n")