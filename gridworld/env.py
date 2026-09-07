from dataclasses import dataclass
from typing import List, Tuple

# Actions: 0 up, 1 right, 2 down, 3 left
ACTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
A_UP, A_RIGHT, A_DOWN, A_LEFT = 0, 1, 2, 3
ALL_ACTIONS = [A_UP, A_RIGHT, A_DOWN, A_LEFT]

# The spec defines rewards for apples/keys/chests but leaves death unvalued.
# Without a negative reward there, Q-learning/SARSA see death as equivalent
# to any other zero-reward step, so nothing steers the policy away from
# hazards - which makes Task 2's "SARSA is more conservative near hazards"
# comparison impossible to satisfy.
DEATH_REWARD = -1.0


@dataclass
class StepResult:
    # (agent_x, agent_y, apple_mask, chest_mask, key_count)
    next_state: Tuple[int, int, int, int, int]
    reward: float
    done: bool
    info: dict


class GridWorld:
    def __init__(self, layout: List[str], monster_move_prob: float = 0.4):
        self.layout = layout
        self.w, self.h = len(layout[0]), len(layout)
        self.monster_move_prob = monster_move_prob

        self.rocks, self.fires = set(), set()
        self.apples, self.apple_index = [], {}
        self.key_positions = []
        self.chests, self.chest_index = [], {}
        self.monsters, self.monster_index = [], {}
        self.start = (0, 0)

        for y, row in enumerate(layout):
            for x, ch in enumerate(row):
                p = (x, y)
                if ch == "A":
                    self.apple_index[p] = len(self.apples)
                    self.apples.append(p)
                elif ch == "S":
                    self.start = p
                elif ch == "R":
                    self.rocks.add(p)
                elif ch == "F":
                    self.fires.add(p)
                elif ch == "K":
                    self.key_positions.append(p)
                elif ch == "C":
                    self.chest_index[p] = len(self.chests)
                    self.chests.append(p)
                elif ch == "M":
                    self.monster_index[p] = len(self.monsters)
                    self.monsters.append(p)
        self.reset()

    def reset(self) -> Tuple[int, int, int, int, int]:
        self.agent = self.start
        self.alive = True
        self.step_count = 0

        self.apple_mask = self._full_mask(len(self.apples))
        self.chest_mask = self._full_mask(len(self.chests))
        self.keys_remaining = set(self.key_positions)
        self.key_count = 0
        self.monster_positions = list(self.monsters)
        return self.encode_state()

    @staticmethod
    def _full_mask(n: int) -> int:
        return (1 << n) - 1 if n > 0 else 0

    def encode_state(self) -> Tuple[int, int, int, int, int]:
        return (self.agent[0], self.agent[1], self.apple_mask, self.chest_mask, self.key_count)

    # movement helpers
    def in_bounds(self, p):
        return 0 <= p[0] < self.w and 0 <= p[1] < self.h

    def blocked(self, p):
        return p in self.rocks

    def try_move(self, p, a):
        dx, dy = ACTIONS[a]
        np_ = (p[0] + dx, p[1] + dy)
        if not self.in_bounds(np_):
            return p
        if self.blocked(np_):
            return p
        return np_

    def _move_monsters(self):
        """Move monsters with probability monster_move_prob.
        Each monster independently has a chance to move randomly to an adjacent tile.
        If a monster moves into the agent, the agent dies.
        """
        import random
        for i, monster_pos in enumerate(self.monster_positions):
            if random.random() < self.monster_move_prob:
                possible_moves = []
                for action in ALL_ACTIONS:
                    new_pos = self.try_move(monster_pos, action)
                    possible_moves.append(new_pos)

                self.monster_positions[i] = random.choice(possible_moves)

                if self.monster_positions[i] == self.agent:
                    self.alive = False

    def step(self, action: int) -> StepResult:
        self.step_count += 1
        reward = 0.0

        # 1) move the agent
        self.agent = self.try_move(self.agent, action)

        # 2) death: fire tile
        if self.agent in self.fires:
            self.alive = False
            return StepResult(self.encode_state(), reward + DEATH_REWARD, True, {"event": "death"})

        # 3) death: monster collision (agent walks into monster)
        if self.agent in self.monster_positions:
            self.alive = False
            return StepResult(self.encode_state(), reward + DEATH_REWARD, True, {"event": "death"})

        # 4) apple collection
        if self.agent in self.apple_index:
            idx = self.apple_index[self.agent]
            if (self.apple_mask >> idx) & 1:
                self.apple_mask &= ~(1 << idx)
                reward += 1.0

        # 5) key pickup (no reward, just inventory)
        if self.agent in self.keys_remaining:
            self.keys_remaining.discard(self.agent)
            self.key_count += 1

        # 6) chest opening (needs a key)
        if self.agent in self.chest_index:
            idx = self.chest_index[self.agent]
            if (self.chest_mask >> idx) & 1 and self.key_count > 0:
                self.chest_mask &= ~(1 << idx)
                self.key_count -= 1
                reward += 2.0

        # 7) move monsters (40% chance each to move randomly)
        self._move_monsters()

        # 8) death: monster moves into agent
        if self.agent in self.monster_positions:
            self.alive = False
            return StepResult(self.encode_state(), reward + DEATH_REWARD, True, {"event": "death"})

        # 9) episode ends once every collectible reward is gone
        done = self.apple_mask == 0 and self.chest_mask == 0
        return StepResult(self.encode_state(), reward, done, {})
