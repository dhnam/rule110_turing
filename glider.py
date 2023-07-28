from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    LEFT = -1
    STOP = 0
    RIGHT = 1

@dataclass(unsafe_hash=True)
class Glider:
    speed: int # make sure speed is 1 when move_dir is STOP. Bigger = Slower
    move_dir: Direction
    subtype: int = 0

G_TABLE_0 = Glider(1, Direction.LEFT, 0)
G_TABLE_1 = Glider(1, Direction.LEFT, 1)
G_LEADER = Glider(1, Direction.LEFT, 2)
G_TAPE_0 = Glider(1, Direction.STOP, 0)
G_TAPE_1 = Glider(1, Direction.STOP ,1)
G_ACCEPT = Glider(1, Direction.RIGHT, 0)
G_REJECT = Glider(1, Direction.RIGHT, 1)
G_OSSIFY = Glider(1, Direction.RIGHT, 2)

class GliderSystem:
    # For only Cyclic tag system, it is.
    def __init__(self):
        self.sparse_tape: list[list[int | Glider]] = [] # TODO tuple[int, Glider]? list[int|Glider]? tuple[list[int], Glider]?
        self.collision: dict[frozenset[Glider, Glider], list[Glider]] = {
            frozenset([G_OSSIFY, G_TABLE_0]): [G_TAPE_0],
            frozenset([G_OSSIFY, G_TABLE_1]): [G_TAPE_1],
            frozenset([G_REJECT, G_TABLE_0]): [G_REJECT],
            frozenset([G_REJECT, G_TABLE_1]): [G_REJECT],
            frozenset([G_REJECT, G_LEADER]): [G_LEADER],
            frozenset([G_ACCEPT, G_TABLE_0]): [G_ACCEPT, G_TABLE_0],
            frozenset([G_ACCEPT, G_TABLE_1]): [G_ACCEPT, G_TABLE_1],
            frozenset([G_ACCEPT, G_LEADER]): [G_LEADER],
            frozenset([G_TAPE_1, G_LEADER]): [G_ACCEPT],
            frozenset([G_TAPE_0, G_LEADER]): [G_REJECT],
            frozenset([G_TAPE_0, G_TABLE_0]): [G_TAPE_0, G_TABLE_0],
            frozenset([G_TAPE_0, G_TABLE_1]): [G_TAPE_0, G_TABLE_1],
            frozenset([G_TAPE_1, G_TABLE_0]): [G_TAPE_1, G_TABLE_0],
            frozenset([G_TAPE_1, G_TABLE_1]): [G_TAPE_1, G_TABLE_1],
        } # Glider system collision table for cyclic tag system.
        self.gun: list[tuple[Glider, int, int]] = []
        self.gun_counter: list[int] = []
    
    def update(self):
        for next_glider in self.sparse_tape:
            next_glider[0] += next_glider[1].move_dir * next_glider[1].speed
        self.sparse_tape: list[list[int | Glider]] = sorted(self.sparse_tape, lambda x: x[0])
        new_list = []
        for next_place in self.sparse_tape:
            if new_list[-1][0] == next_place[0]:
                next_glider = self.collision[frozenset(new_list[-1][1], next_place[1])]
                new_list[-1] = [next_place[0], next_glider]
            else:
                new_list.append(next_place)
        for i, ((g_type, place, freq), counter) in enumerate(zip(self.gun, self.gun_counter)):
            if counter == 0:
                self.sparse_tape.append([place, g_type])
                self.gun_counter[i] = freq
            else:
                self.gun_counter[i] -= 1
        
        self.sparse_tape: list[list[int | Glider]] = sorted(self.sparse_tape, lambda x: x[0])
    
    def add_gun(self, g_type: Glider, place: int, freq: int):
        self.gun.append((g_type, place, freq))
        self.gun_counter.append(freq)
        
if __name__ == "__main__":
    pass