# A3 - GridWorld RL (Part I)

Q-learning and SARSA in a visual Pygame gridworld, covering Tasks 1-3 of the
assignment spec ([spec.md](spec.md), rubric in [rubric.md](rubric.md)).
Tasks 4 (monster levels) and 5 (intrinsic reward) are out of scope for this
project.

## Setup

```bash
pip install -r requirements.txt
```

## Running the game

```bash
python main.py
```

Title screen -> **Play** -> pick a level -> (Levels 2-3 only) pick
**Q-Learning** or **SARSA** -> training runs live in a Pygame window.

**Controls during training:** `V` toggles fast/visual mode, `R` resets the
current run, closing the window quits the app.

## Levels

| Level | Task | Mechanics | Algorithm |
|---|---|---|---|
| 0 | 1 | Apples only | Q-learning (fixed) |
| 1 | 2 | Cliff-walk layout (fire row = short path, safe route over the top) | SARSA (fixed) |
| 2 | 3 | Multiple apples, key, chest | Q-learning or SARSA |
| 3 | 3 | Same as Level 2 + rocks (longer route) | Q-learning or SARSA |

Level 1's layout is deliberately the classic "cliff walk": the shortest path
runs beside instant-death fire tiles, and there's a longer safe route above
it. This is what makes Q-learning vs. SARSA actually diverge (Q-learning
tends to hug the cliff; SARSA keeps its distance) instead of learning
identical policies.

## Design notes

- **Death reward.** The spec defines rewards for apples/keys/chests but never
  assigns one to death. Leaving it at 0 (same as any non-rewarding step)
  makes death indistinguishable from an ordinary move, so Q-learning/SARSA
  have no gradient pushing them away from hazards - which makes Task 2's
  "SARSA is more conservative near hazards" comparison impossible to actually
  demonstrate. `DEATH_REWARD = -1.0` in [gridworld/env.py](gridworld/env.py)
  fills that gap; it's an addition where the spec is silent, not a change to
  a value the spec specifies.
- **Terminal-state masking.** Both update rules zero out the bootstrap term
  (`gamma * Q(next_state)`) when the transition ends the episode - a
  terminal state has no future reward to bootstrap from. Missing this made
  death and success both silently blend into whatever the next state's
  (irrelevant) Q-values happened to be, and combined with the missing death
  reward above, made Level 1 (cliff walk) fail to converge at all in
  testing - success rate stayed near 0% even after 600 episodes. With both
  fixes, Q-learning and SARSA converge to ~98-100% success within a few
  hundred episodes.

## Project layout

```
gridworld/
  env.py            GridWorld environment (rules, step/reset)
  agents.py         QTable, epsilon-greedy, Q-learning & SARSA updates
  render.py         Pygame drawing (tiles, agent, HUD)
  levels.py         Level layouts (LEVELS dict, keyed by level id)
  config.py         Config loader (defaults + optional per-level JSON)
  train.py          Shared training loop (used by both the game and experiments)
  ui.py             Menu Button widget
  logging_utils.py  Per-episode CSV logger
config/
  config_level0.json ... config_level3.json   Per-level training parameters
main.py             Game entry point (menu -> level -> training)
run_experiment.py   Headless training run -> CSV (for report evidence)
plot_curves.py      Overlay CSVs into a comparison PNG
logs/               Example training-curve CSVs
report_assets/      Example comparison plots for the report
```

## Config files

Each `config/config_level{N}.json` overrides the defaults in
[gridworld/config.py](gridworld/config.py) for that level; any key you omit
falls back to the default. Missing file = defaults are used.

| Key | Meaning |
|---|---|
| `episodes` | Number of training episodes |
| `alpha` | Learning rate |
| `gamma` | Discount factor (how much future reward matters) |
| `epsilonStart` / `epsilonEnd` | Exploration rate at the start / end of decay |
| `epsilonDecayEpisodes` | Episodes over which epsilon linearly decays |
| `maxStepsPerEpisode` | Step cap before an episode is force-ended |
| `fpsVisual` / `fpsFast` | Render speed caps for the two visualize modes (game only) |
| `tileSize` | Pixel size per grid cell (visual only) |
| `seed` | RNG seed, for reproducible runs |

## Generating report evidence (training curves)

`run_experiment.py` trains headlessly (no window, full speed) and logs each
episode's return to CSV:

```bash
python run_experiment.py --level 1 --algorithm qlearning --out logs/level1_qlearning.csv
python run_experiment.py --level 1 --algorithm sarsa --out logs/level1_sarsa.csv
```

`--episodes N` overrides the config's episode count without editing the file.

Then overlay any set of CSVs into one comparison plot:

```bash
python plot_curves.py logs/level1_qlearning.csv:Q-learning logs/level1_sarsa.csv:SARSA \
    --title "Level 1: Q-learning vs SARSA" --out report_assets/level1_comparison.png
```

## Status

- **Part I:** implemented - gridworld, Q-learning, SARSA, Levels 0-3,
  config-driven training, evidence pipeline. Tasks 4/5 (monsters, intrinsic
  reward) intentionally out of scope.
- **Part II (deep RL arena):** not started yet.
- **Report / video demo:** not started yet.
