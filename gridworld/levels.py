# Level layouts. Each layout is a list of equal-length row strings.
# S = start, A = apple, R = rock, F = fire, K = key, C = chest, M = monster.

# Task 1 - apples only, straight run to the goal.
LEVEL0 = [
    "S           ",
    "            ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   ",
    "        A   ",
]

# Task 2 - classic "cliff walk": a fire-lined row is the shortest route from
# S to A, with a longer safe route over the top. Q-learning tends to hug the
# cliff (it assumes optimal play), while SARSA factors in its own epsilon-greedy
# exploration risk and learns to keep more distance from the fire.
LEVEL1 = [
    "            ",
    "            ",
    "            ",
    "SFFFFFFFFFFA",
]

# Task 3 - multiple apples, a key, and a chest, no hazards.
LEVEL2 = [
    "S           ",
    "  A         ",
    "        K   ",
    "  A         ",
    "        C   ",
    "  A         ",
    "            ",
    "            ",
]

# Task 3 - same objects as Level 2, plus rocks to force longer routes.
LEVEL3 = [
    "S           ",
    "   A        ",
    "  RRRR      ",
    "        K   ",
    "  RRRR      ",
    "   A        ",
    "          C ",
    "   A        ",
]

# Task 4 - apples guarded by wandering monsters (40% move chance per step).
LEVEL4 = [
    "S           ",
    "            ",
    "      M     ",
    "  A         ",
    "        A   ",
    "            ",
    "      M     ",
    "  A         ",
]

# Task 4 - monsters plus a key/chest objective, for a harder monster level.
LEVEL5 = [
    "S           ",
    "  RRRR      ",
    "        K   ",
    "  A     M   ",
    "  RRRR      ",
    "  A         ",
    "        M   ",
    "          C ",
]

# Task 5 - a single long winding corridor (boustrophedon maze). The reward is
# far from the start with no shortcuts, which is exactly the sparse-reward
# setting intrinsic reward (state-visit bonus) is meant to help with.
LEVEL6 = [
    "S           ",
    "RRRRRRRRRRR ",
    "            ",
    " RRRRRRRRRRR",
    "            ",
    "RRRRRRRRRRR ",
    "            ",
    " RRRRRRRRRRR",
    "           A",
]

LEVELS = {
    0: LEVEL0,
    1: LEVEL1,
    2: LEVEL2,
    3: LEVEL3,
    4: LEVEL4,
    5: LEVEL5,
    6: LEVEL6,
}


def get_level(level_id: int):
    layout = LEVELS[level_id]
    width = max(len(row) for row in layout)
    return [row.ljust(width)[:width] for row in layout]
