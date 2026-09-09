# How to Test the Game - Levels 0-6

## Quick Start

```bash
python3 main.py
```

This launches the interactive Pygame menu.

---

## Menu Navigation

### Title Screen
- **Play** - Go to level select
- **Exit** - Quit the game

### Level Select Screen
- **Level 0** - Q-Learning (Task 1) - Apples only
- **Level 1** - SARSA (Task 2) - Cliff walk (fire hazards)
- **Level 2** - Key & Chest (Task 3) - Pick algorithm
- **Level 3** - Key & Chest+ (Task 3) - With rocks
- **Level 4** - Monster (Simple) (Task 4) - 1 monster, learning to avoid
- **Level 5** - Monster (Complex) (Task 4) - 2 monsters, complex navigation
- **Level 6** - Intrinsic Reward (Task 5) - Curiosity-driven learning

### Algorithm Select (for Levels 2-3, 6)
- **Q-Learning** - Off-policy, learns optimal policy
- **SARSA** - On-policy, more conservative (closer to fire)
- **Back** - Return to level select

---

## Controls During Training

| Key | Action |
|-----|--------|
| `V` | Toggle between Visual mode (slower, see every frame) and Fast mode (speed up rendering) |
| `R` | Reset the current training run (restart from episode 1) |
| `ESC` / Close Window | Quit the game |

---

## What to Look For

### Level 0 - Q-Learning (Apples Only)
- Agent learns to move right towards apples
- Returns should increase quickly
- By episode ~200, agent should collect all 3 apples consistently

### Level 1 - SARSA (Cliff Walk)
- Two paths: short path beside fire (risky) vs longer safe path
- SARSA should learn the safe path (more conservative)
- Q-Learning would hug the cliff more aggressively

### Levels 2-3 - Multiple Items
- Agent must collect apples first
- Then find key
- Then open chest for +2 reward
- More complex, slower convergence

### Level 4 - Simple Monster (NEW!)
- 1 purple monster moving around (40% chance each step)
- Agent learns to avoid monster while collecting apples
- Watch for agent taking detours around monster

### Level 5 - Complex Monster (NEW!)
- 2 monsters, more rocks
- Harder navigation required
- Agent must learn complex avoidance paths
- Returns will be noisier due to stochasticity

### Level 6 - Intrinsic Reward (NEW!)
- Same setup as Level 5
- Agent should explore more due to intrinsic reward
- Watch for agent visiting varied areas of the map

---

## Visual Elements

| Color | Element |
|-------|---------|
| Green (agent) | The learner (square) |
| Red (apple) | +1 reward (circle) |
| Orange (fire) | Death hazard, -1 reward (triangle) |
| Purple (monster) | Moving hazard, -1 on collision (circle) |
| Gray (rock) | Blocks movement (square) |
| Yellow (key) | Unlock chest (circle) |
| Brown (chest) | +2 reward when opened (square) |

---

## HUD Information

During training, you'll see:

```
Ep 45/800  step 23  eps 0.925  Q-LEARNING
Apples left 3  Monsters 1
Return 2.50  Level 4 - Monster (Simple)
V toggles fast mode. R resets.
```

- **Ep 45/800** - Current episode / total episodes
- **step 23** - Steps taken in this episode
- **eps 0.925** - Current exploration rate (epsilon)
- **Q-LEARNING / SARSA** - Algorithm in use
- **Apples left 3** - Number of remaining apples
- **Monsters 1** - Number of monsters on this level
- **Return 2.50** - Total reward accumulated this episode

---

## Performance Indicators

### Good Learning:
- Returns increase gradually
- By mid-training, agent should have positive returns most episodes
- Fewer steps needed per episode (more efficient)
- Epsilon decreases over time (less random exploration)

### Monster Levels (4-5):
- First episodes: agent often dies to monsters
- Mid-training: agent learns to avoid
- Late training: agent successfully navigates around monsters and collects rewards

### Intrinsic Reward (Level 6):
- Agent explores more areas compared to Level 5
- May take longer to converge but explores more thoroughly
- Returns might be more consistent (less variance)

---

## Testing Checklist

- [ ] Level 0: Agent learns to move right, collects apples
- [ ] Level 1: SARSA learns safe path (less aggressive than Q-Learning would be)
- [ ] Level 2-3: Agent collects multiple items in correct order (apples → key → chest)
- [ ] Level 4: Agent learns to avoid single monster
- [ ] Level 5: Agent navigates around 2 monsters + rocks
- [ ] Level 6: Agent explores with intrinsic reward
- [ ] Fast mode (V key) runs much faster
- [ ] Reset (R key) restarts training from episode 0
- [ ] Close window cleanly without errors

---

## Common Issues

**Game freezes?**
- Normal - training is running, especially in visual mode
- Press V to switch to fast mode for faster training

**Agent not moving?**
- First few episodes might have low returns due to random exploration
- Keep watching - it should improve after 10-20 episodes

**Monster doesn't move?**
- Monsters move with 40% probability each step
- Watch longer - you'll see it move eventually
- Or press V to speed up and see movement clearer

**Agent dies to monsters immediately?**
- This is correct! Agent starts with random exploration
- It learns to avoid over time
- By episode 100-200, it should avoid successfully

---

## Next Steps After Testing

1. ✅ Verify game runs for all 7 levels
2. ✅ Verify agents learn and return values increase
3. ✅ Verify monsters move and collisions work
4. ✅ Ready to generate training curves with `run_experiment.py`

---

## Headless Training (No GUI)

If you just want to generate data without the GUI:

```bash
python run_experiment.py --level 4 --algorithm qlearning --out logs/level4.csv
```

This runs training at full speed without rendering.

---

**Happy testing!** 🎮
