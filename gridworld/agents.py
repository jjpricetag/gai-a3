import random
from typing import Dict, Tuple

from .env import ALL_ACTIONS


class QTable:
    def __init__(self):
        self.q: Dict[Tuple[Tuple[int, int, int], int], float] = {}

    def get(self, s, a):
        return self.q.get((s, a), 0.0)

    def set(self, s, a, v):
        self.q[(s, a)] = v

    def best_value(self, s):
        return max(self.get(s, a) for a in ALL_ACTIONS)

    def best_actions(self, s):
        vals = [self.get(s, a) for a in ALL_ACTIONS]
        m = max(vals)
        return [a for a, v in zip(ALL_ACTIONS, vals) if v == m]


def linear_epsilon(ep, start, end, decay_ep):
    if decay_ep <= 0:
        return end
    t = min(ep / decay_ep, 1.0)
    return start + t * (end - start)


def epsilon_greedy(qtab: QTable, s, eps):
    if random.random() < eps:
        return random.choice(ALL_ACTIONS)
    best = qtab.best_actions(s)
    return random.choice(best)


def q_learning_update(qtab: QTable, s, a, r, sp, alpha, gamma, done=False):
    """Off-policy: bootstraps from the best possible action at sp.

    A terminal transition (episode ended at sp) has no future value, so the
    bootstrap term must be zeroed out there - otherwise a death is wrongly
    valued using sp's Q-values as if play continued past it.
    """
    current = qtab.get(s, a)
    future = 0.0 if done else qtab.best_value(sp)
    target = r + gamma * future
    qtab.set(s, a, current + alpha * (target - current))


def sarsa_update(qtab: QTable, s, a, r, sp, ap, alpha, gamma, done=False):
    """On-policy: bootstraps from the action actually chosen at sp (terminal-masked, see above)."""
    current = qtab.get(s, a)
    future = 0.0 if done else qtab.get(sp, ap)
    target = r + gamma * future
    qtab.set(s, a, current + alpha * (target - current))
