"""
Orbit Wars — Main Agent
=======================
The agent() function is called every turn by the game engine.

SUBMISSION INSTRUCTIONS:
  The function signature must stay: def agent(obs)
"""

import math


# ─────────────────────────────────────────────
#  PLANET / FLEET field indices  (read-only)
# ─────────────────────────────────────────────
# Planet  → [id, owner, x, y, radius, ships, production]
P_ID    = 0
P_OWN   = 1
P_X     = 2
P_Y     = 3
P_RAD   = 4
P_SHIPS = 5
P_PROD  = 6

# Fleet   → [id, owner, x, y, angle, from_planet_id, ships]
F_ID    = 0
F_OWN   = 1
F_X     = 2
F_Y     = 3
F_ANG   = 4
F_FROM  = 5
F_SHIPS = 6


# ─────────────────────────────────────────────
#  TUNABLE PARAMETERS  ← tweak these first
# ─────────────────────────────────────────────
GARRISON_RATIO   = 0.5   # keep this fraction of ships as defenders (0.5 = keep half)
MIN_SEND         = 5     # never send fewer than this many ships
ATTACK_THRESHOLD = 1.2   # only attack if we can send 1.2× the target's garrison


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def dist(ax, ay, bx, by):
    """Euclidean distance between two points."""
    return math.hypot(bx - ax, by - ay)


def angle_to(src, tgt):
    """Angle in radians from planet src to planet tgt."""
    return math.atan2(tgt[P_Y] - src[P_Y], tgt[P_X] - src[P_X])


def ships_available(planet):
    """How many ships this planet can safely spare this turn."""
    return int(planet[P_SHIPS] * (1 - GARRISON_RATIO))


def target_score(src, tgt):
    """
    Lower score = better target.
    Rewards: close distance, low defenders, high production.
    """
    d = dist(src[P_X], src[P_Y], tgt[P_X], tgt[P_Y])
    defenders = tgt[P_SHIPS]
    production = tgt[P_PROD]
    return d + defenders * 3 - production * 20


# ─────────────────────────────────────────────
#  STRATEGY MODULES
#  Each returns a list of moves: [[from_id, angle, ships], ...]
# ─────────────────────────────────────────────

def expand(me, my_planets, neutral_planets):
    """
    EXPAND: capture nearby neutral planets.
    Priority: close + low defenders + high production.
    """
    moves = []
    already_targeted = set()

    for src in sorted(my_planets, key=lambda p: -p[P_SHIPS]):
        available = ships_available(src)
        if available < MIN_SEND:
            continue

        # Filter neutrals not already being targeted
        candidates = [t for t in neutral_planets if t[P_ID] not in already_targeted]
        if not candidates:
            break

        # Pick best target
        tgt = min(candidates, key=lambda t: target_score(src, t))

        # Only attack if we have enough ships to actually win
        needed = int(tgt[P_SHIPS] * ATTACK_THRESHOLD) + 1
        send = min(available, src[P_SHIPS] - 1)  # keep at least 1 defender

        if send >= needed:
            moves.append([src[P_ID], angle_to(src, tgt), send])
            already_targeted.add(tgt[P_ID])

    return moves


def attack(me, my_planets, enemy_planets):
    """
    ATTACK: assault enemy planets when we have a clear advantage.
    Only commits if we can send significantly more than the garrison.
    """
    moves = []
    already_targeted = set()

    for src in sorted(my_planets, key=lambda p: -p[P_SHIPS]):
        available = ships_available(src)
        if available < MIN_SEND:
            continue

        candidates = [t for t in enemy_planets if t[P_ID] not in already_targeted]
        if not candidates:
            break

        # Pick weakest enemy planet
        tgt = min(candidates, key=lambda t: t[P_SHIPS])

        needed = int(tgt[P_SHIPS] * ATTACK_THRESHOLD) + 1
        send = min(available, src[P_SHIPS] - 1)

        if send >= needed:
            moves.append([src[P_ID], angle_to(src, tgt), send])
            already_targeted.add(tgt[P_ID])

    return moves


def reinforce(me, my_planets):
    """
    REINFORCE: send ships from rich planets to weak/exposed planets.
    Helps defend planets that are low on garrison.
    """
    moves = []
    if len(my_planets) < 2:
        return moves

    # Find richest sender and weakest receiver
    sender   = max(my_planets, key=lambda p: p[P_SHIPS])
    receiver = min(my_planets, key=lambda p: p[P_SHIPS])

    if sender[P_ID] == receiver[P_ID]:
        return moves

    available = ships_available(sender)
    # Only reinforce if sender has lots of ships and receiver is really low
    if available >= 20 and receiver[P_SHIPS] < 10:
        send = available // 2
        moves.append([sender[P_ID], angle_to(sender, receiver), send])

    return moves


# ─────────────────────────────────────────────
#  MAIN AGENT FUNCTION  ← Kaggle calls this
# ─────────────────────────────────────────────

def agent(obs):
    """
    Called every turn. Returns a list of moves.
    Each move: [from_planet_id, direction_angle, num_ships]
    """

    # ── Parse observation ──────────────────────
    me      = obs.get("player", 0)
    planets = obs.get("planets", [])
    fleets  = obs.get("fleets",  [])

    if not planets:
        return []

    # ── Categorise planets ─────────────────────
    my_planets      = [p for p in planets if p[P_OWN] == me]
    neutral_planets = [p for p in planets if p[P_OWN] == -1]
    enemy_planets   = [p for p in planets if p[P_OWN] not in (me, -1)]

    if not my_planets:
        return []  # eliminated — nothing to do

    # ── Decide strategy this turn ──────────────
    moves = []

    # Priority 1: expand into neutrals (cheap, safe gains)
    if neutral_planets:
        moves += expand(me, my_planets, neutral_planets)

    # Priority 2: attack enemies if neutrals exhausted or we're strong
    if enemy_planets and (not neutral_planets or len(my_planets) > 3):
        moves += attack(me, my_planets, enemy_planets)

    # Priority 3: reinforce weak planets
    if not moves:
        moves += reinforce(me, my_planets)

    return moves