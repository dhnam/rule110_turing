# Assemble everything to make turing machine

from typing import Callable, TypeVar
from turing_to_tag import *
from tag_to_cyclic import *
import math

Parent = TypeVar('Parent')
Child = TypeVar('Child')
Info = TypeVar('Info')

class Nester:
    def __init__(self, base:object):
        self.base = base
        self.reg_chain:list[Callable[[Parent,], Child]] = []
        self.info_reg_chain: list[Callable[[Parent, ], Info] | None] = []
        self.infos: list[Info] = []
        self.conditions: list[Callable[[Child,], bool]] = []
        self.objs: list[object] = []
        
    def register(
        self,
        transform_func: Callable[[Parent,], Child],
        info_func: Callable[[Parent, ], Info] | None,
        condition_func: Callable[[Child, ], bool],
    ):
        self.reg_chain.append(transform_func)
        self.info_reg_chain.append(info_func)
        self.conditions.append(condition_func)
        
    def generate(self):
        self.objs = []
        next_obj = self.base
        for next_chain, next_info_chain in zip(self.reg_chain, self.info_reg_chain):
            if next_info_chain is None:
                self.infos.append(None)
            else:
                next_info = next_info_chain(next_obj)
                self.infos.append(next_info)
            next_obj = next_chain(next_obj)
            self.objs.append(next_obj)
            
    def __iter__(self):
        return self
    
    def __next__(self):
        next(self.base)
        prev_count: list[int] = [1]
        for i, next_obj in enumerate(self.objs):
            counter = 0
            for _ in range(math.prod(prev_count)):
                next(next_obj)
                counter += 1
                while not self.conditions[i](next_obj):
                    next(next_obj)
                    counter += 1
            prev_count.append(counter)
        return self.base, self.objs, prev_count
    
    def __str__(self) -> str:
        string = ""
        string += f"====BASE ({type(self.base).__name__})====\n"
        string += str(self.base)
        string += "\n"
        for next_obj in self.objs:
            string += f"==={type(next_obj).__name__}===\n"
            string += str(next_obj)
            string += "\n"
        return string
    
    def compare(self) -> list[bool]:
        prev_obj = self.base
        res = []
        for next_chain, next_obj in zip(self.reg_chain, self.objs):
            next_compare = next_chain(prev_obj)
            print(next_compare)
            res.append(next_obj == next_compare)
            prev_obj = next_obj
        return res
                

if __name__ == "__main__":
    example_turing_table = TuringTransitionTable([TuringStateTransition(
        0,
        (
            TuringTransition(TuringSymbol.ONE, TuringDirection.RIGHT, 0),
            TuringTransition(TuringSymbol.ZERO, TuringDirection.RIGHT, 0)
        )
    )])

    example_tape_state = TuringTapeTuple(
        state=0,
        left_number=5,
        right_number=21,
        head=TuringSymbol.ONE,
    )

    example_turing_machine = BinaryTuring(
        example_turing_table, BinaryTuringTape.from_tape_tuple(example_tape_state))

    print(example_turing_machine)
    nester = Nester(example_turing_machine)
    nester.register(turing_machine_to_tag_system, None, is_step_passed)
    nester.register(tag_system_to_cyclic_machine, tag_system_to_cyclic_tags_dict, is_tag_step_passed)
    nester.generate()
    print(nester)
    print(nester.compare())
    next(nester)
    print(nester)
    print(nester.compare())
    print(nester.infos)