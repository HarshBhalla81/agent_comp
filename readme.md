# Orbit Wars — Your Agent Project

## Folder structure

```
orbit_wars/
│
├── agent/
│   └── main.py          ← THE FILE YOU SUBMIT TO KAGGLE
│
├── versions/            ← auto-saved snapshots (never delete)
│   └── 20260421_...py
│
├── logs/                ← put test output here if needed
│
├── tests/               ← put custom test scripts here
│
├── test_locally.py      ← run this to test before submitting
├── save_version.py      ← run this before every change
└── README.md
```

---

## How to run your agent locally

```bash
# Basic test (200 turns, 1 game)
python test_locally.py

# More turns
python test_locally.py --turns 500

# See every single turn
python test_locally.py --verbose

# Run 10 games with different maps and see win rate
python test_locally.py --games 10
```

---

## Your improvement workflow (repeat every time)

```
Step 1.  python save_version.py "describe what it does now"
Step 2.  Edit agent/main.py
Step 3.  python test_locally.py --games 5
Step 4.  If win rate improved → go to step 1 again
         If win rate dropped  → open versions/ and copy back the old file
Step 5.  Upload agent/main.py to Kaggle when ready
```

---

## What to improve (in order of difficulty)

### Week 1 — Easy wins
- [ ] Tune GARRISON_RATIO (try 0.3, 0.4, 0.6)
- [ ] Tune ATTACK_THRESHOLD (try 1.0, 1.5, 2.0)
- [ ] Target high-production planets first, not just closest
- [ ] Launch from multiple planets simultaneously at same target

### Week 2 — Medium
- [ ] Detect incoming enemy fleets and reinforce the threatened planet
- [ ] Don't attack a planet if a friendly fleet is already heading to it
- [ ] Keep a stronger garrison on the home planet specifically

### Week 3-4 — Hard
- [ ] Predict orbiting planet positions using angular velocity
- [ ] Coordinate all planets toward one enemy in a combined assault
- [ ] Early vs late game switch (expand early, attack late)

### Week 5-6 — Advanced
- [ ] Track enemy behavior and adapt
- [ ] Multi-target strategy: feint on one planet, real attack on another
- [ ] Look-ahead: simulate 5-10 turns before deciding

---

## Key planet/fleet field reference

```python
# Planet = [id, owner, x, y, radius, ships, production]
#           [0]   [1]  [2] [3]  [4]    [5]      [6]
#
# owner: 0-3 = player ID,  -1 = neutral
# ships: current garrison
# production: ships generated per turn when owned

# Fleet = [id, owner, x, y, angle, from_planet_id, ships]
#          [0]   [1]  [2] [3]  [4]       [5]          [6]
```

---

## Submitting to Kaggle

1. Go to the competition page
2. Click "Code" tab → "New Notebook"
3. Copy-paste the contents of `agent/main.py` into the notebook
4. Make sure the file is named `main.py` in the submission
5. Submit — your first game plays within minutes