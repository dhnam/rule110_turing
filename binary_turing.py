"""Turing machine with two symbols.
Simplest Turing machine, and our ultimate goal is simulate this using Rule 110.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from collections.abc import Mapping

TuringState = int

class TuringSymbol(Enum):
    """Enum for Symbols of Turing machine
    """
    ZERO = 0
    ONE = 1
    
class TuringDirection(Enum):
    """Enum for Direction of Turing machine
    """
    RIGHT = 0
    LEFT = 1

@dataclass
class TuringTransition:
    """Dataclass for Transition of Turing machine
    """
    write: TuringSymbol
    move: TuringDirection
    next_state: TuringState

@dataclass
class TuringStateTransition:
    """Dataclass for State and transitions of Turing machine
    """
    state: TuringState
    transitions: tuple[TuringTransition, TuringTransition]
    

@dataclass
class TuringTapeTuple:
    """Dataclass representing state of Tape of turing machine
    """
    state: TuringState
    left_number: int
    right_number: int
    head: TuringSymbol

class TransitionTable(Mapping[TuringState, TuringStateTransition]):
    """Transition Table for Turing machine. Can be used like read-only dictionary.
    """
    def __init__(self, states: list[TuringStateTransition]):
        self.state_table: dict[TuringState, TuringStateTransition] = {}
        for next_state in states:
            assert next_state.state not in self.state_table
            self.state_table[next_state.state] = next_state
    
    def __getitem__(self, key: TuringState) -> TuringStateTransition:
        return self.state_table[key]
    
    def __iter__(self):
        return iter(self.state_table)

    def __len__(self):
        return len(self.state_table)
    
class BinaryTuringTape:
    def __init__(self, tape: list[TuringSymbol|int]|None = None):
        self.tape: list[TuringSymbol] = []
        if tape is not None:
            self.tape = [TuringSymbol.ONE if x == 1 else TuringSymbol.ZERO for x in tape]
        self.head: int = 0
        self.tape_offset: int = 0
        
    @property
    def _head_addr(self) -> int:
        return self.head - self.tape_offset
    
    @property
    def head_symbol(self) -> TuringSymbol:
        """Get symbol on tape pointed by head

        Returns:
            TuringSymbols: Symbol pointed
        """
        return self.tape[self._head_addr]
    
    @head_symbol.setter
    def head_symbol(self, value: TuringSymbol):
        self.tape[self._head_addr] = value
        
    def _move_left(self):
        self.head -= 1
        if self.head < self.tape_offset:
            self.tape_offset -= 1
            self.tape.insert(0, TuringSymbol.ZERO)

    def _move_right(self):
        if self.head == self.tape_offset and self.tape[0] == TuringSymbol.ZERO:
            self.tape.pop(0)
            self.tape_offset += 1
        self.head += 1
        if self._head_addr >= len(self.tape):
            self.tape.append(TuringSymbol.ZERO)

    def move_tape(self, direction: TuringDirection):
        """Move tape for respective direction

        Args:
            direction (TuringDirection): direction to move
        """
        if direction == TuringDirection.LEFT:
            self._move_left()
        else:
            self._move_right()
            
    @classmethod
    def from_tape_tuple(cls, tape_tuple: TuringTapeTuple) -> BinaryTuringTape:
        new_tape: BinaryTuringTape = object.__new__(cls)
        new_tape.__init__()
        left_length = tape_tuple.left_number.bit_length()
        # TODO fix logic
        for i in range(left_length, 0, -1):
            print(i, tape_tuple.left_number, tape_tuple.left_number.bit_length())
            if i == tape_tuple.left_number.bit_length():
                new_tape.tape.append(TuringSymbol.ONE)
                tape_tuple.left_number >>= 1
            else:
                new_tape.tape.append(TuringSymbol.ZERO)
        return new_tape

class BinaryTuring:
    def __init__(self, table: TransitionTable, tape: list[TuringSymbol|int]|None = None):
        self.tape: list[TuringSymbol] = []
        if tape is not None:
            self.tape = [TuringSymbol.ONE if x == 1 else TuringSymbol.ZERO for x in tape]
        self.head: int = 0
        self.tape_offset: int = 0
        self.table = table
        self.state: TuringState = 0

    def _move_left(self):
        self.head -= 1
        if self.head < self.tape_offset:
            self.tape_offset -= 1
            self.tape.insert(0, TuringSymbol.ZERO)

    def _move_right(self):
        if self.head == self.tape_offset and self.tape[0] == TuringSymbol.ZERO:
            self.tape.pop(0)
            self.tape_offset += 1
        self.head += 1
        if self._head_addr >= len(self.tape):
            self.tape.append(TuringSymbol.ZERO)

    def move_tape(self, direction: TuringDirection):
        """Move tape for respective direction

        Args:
            direction (TuringDirection): direction to move
        """
        if direction == TuringDirection.LEFT:
            self._move_left()
        else:
            self._move_right()
            
    @property
    def _head_addr(self) -> int:
        return self.head - self.tape_offset
            
    @property
    def head_symbol(self) -> TuringSymbol:
        """Get symbol on tape pointed by head

        Returns:
            TuringSymbols: Symbol pointed
        """
        return self.tape[self._head_addr]
    
    @head_symbol.setter
    def head_symbol(self, value: TuringSymbol):
        self.tape[self._head_addr] = value

    def read_tape(self) -> TuringSymbol:
        """Function version of `pointed_symbol`.

        Returns:
            TuringSymbols: Symbol read from tape
        """
        return self.head_symbol
    
    def write_tape(self, value: TuringSymbol):
        """Function version of `pointed_symbol`.
        """
        self.head_symbol = value
        
    
    @property
    def tape_tuple(self) -> TuringTapeTuple:
        """Get TuringTapeTuple of the Turing Machine. This represents current state.

        Returns:
            TuringTapeTuple: Calculated TuringTapeTuple
        """
        left_number: int = 0
        right_number: int = 0
        for i, next_symbol in enumerate(self.tape):
            if i == self._head_addr:
                continue
            if i < self._head_addr:
                left_number <<= 1
                if next_symbol == TuringSymbol.ONE:
                    left_number |= 1
            else:
                if next_symbol == TuringSymbol.ZERO:
                    continue
                right_number |= (1 << (i - self._head_addr - 1))
        return TuringTapeTuple(
            state=self.state,
            left_number=left_number,
            right_number=right_number,
            head=self.head_symbol
        )

    def __str__(self) -> str:
        output_str = str(self.tape_tuple) + "\n"
        for next_symbol in self.tape:
            if next_symbol == TuringSymbol.ONE:
                output_str += "1 "
            else:
                output_str += "0 "
        output_str += "\n"
        output_str += "  " * self._head_addr + "^" + "\n"
        output_str += "state: " + str(self.state) + "\n"
        return output_str
    
    def step(self):
        """Make step of Turing machine
        """
        read = self.read_tape()
        transition: TuringTransition = self.table[self.state].transitions[0 if read == TuringSymbol.ZERO else 1]
        self.write_tape(transition.write)
        self.move_tape(transition.move)
        self.state = transition.next_state


if __name__ == "__main__":
    transition_table = TransitionTable([TuringStateTransition(
        0,
        (
            TuringTransition(TuringSymbol.ONE, TuringDirection.RIGHT, 0),
            TuringTransition(TuringSymbol.ZERO, TuringDirection.RIGHT, 0)
        )
    )])
    tape = BinaryTuringTape.from_tape_tuple(TuringTapeTuple(
        0,
        13,
        12,
        1
    ))
    print(tape.tape)
    tape_init = [0,1,1,1,0,0,1,1]
    machine = BinaryTuring(transition_table, tape_init)
    #print(machine)
    for _ in range(10):
        machine.step()
        #print(machine)