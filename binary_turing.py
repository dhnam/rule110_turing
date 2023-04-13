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


class TuringTransitionTable(Mapping[TuringState, TuringStateTransition]):
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
    """Tape used in Turing machine
    """

    def __init__(self, tape: list[TuringSymbol | int] | None = None):
        self.tape: list[TuringSymbol] = []
        if tape is not None:
            self.tape = [TuringSymbol.ONE if x ==
                         1 else TuringSymbol.ZERO for x in tape]
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
        if self._head_addr == len(self.tape) - 1 and self.tape[-1] == TuringSymbol.ZERO:
            self.tape.pop()
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
        """Build tape from `TuringTapeTuple`. State is ignored.

        Args:
            tape_tuple (TuringTapeTuple): Tape tuple to build with

        Returns:
            BinaryTuringTape: Tape built.
        """
        new_tape: BinaryTuringTape = object.__new__(cls)
        new_tape.__init__() #pylint: disable=unnecessary-dunder-call
        left_number = tape_tuple.left_number
        for i in range(tape_tuple.left_number.bit_length(), 0, -1):
            if i == left_number.bit_length():
                new_tape.tape.append(TuringSymbol.ONE)
                left_number ^= 1 << left_number.bit_length() - 1
            else:
                new_tape.tape.append(TuringSymbol.ZERO)
        new_tape.tape.append(tape_tuple.head)
        new_tape.head = tape_tuple.left_number.bit_length()
        right_number = tape_tuple.right_number
        for i in range(tape_tuple.right_number.bit_length(), 0, -1):
            if right_number & 1 == 0:
                new_tape.tape.append(TuringSymbol.ZERO)
            else:
                new_tape.tape.append(TuringSymbol.ONE)
            right_number >>= 1
        return new_tape

    @property
    def left_number(self) -> int:
        """'Left number' of the tape.
        Binary number built with symbols placed at the left side of the head.

        Returns:
            int : calculated number
        """
        left_number: int = 0
        for i, next_symbol in enumerate(self.tape):
            if i < self._head_addr:
                left_number <<= 1
                if next_symbol == TuringSymbol.ONE:
                    left_number |= 1
            else:
                break
        return left_number

    @property
    def right_number(self) -> int:
        """'Right number' of the tape.
        Binary number built with symbols placed at the right side of the head.

        Returns:
            int : calculated number
        """
        right_number: int = 0
        for i, next_symbol in enumerate(self.tape):
            if i > self._head_addr and next_symbol != TuringSymbol.ZERO:
                right_number |= (1 << (i - self._head_addr - 1))
        return right_number

    def __str__(self) -> str:
        output_str: str = ""
        for next_symbol in self.tape:
            if next_symbol == TuringSymbol.ONE:
                output_str += "1 "
            else:
                output_str += "0 "
        output_str += "\n"
        output_str += "  " * self._head_addr + "^"
        return output_str


class BinaryTuring:
    """Turing machine with two states.
    """
    def __init__(
            self,
            table: TuringTransitionTable,
            tape: BinaryTuringTape | list[int | TuringSymbol] | None = None
        ):
        if tape is None:
            self.tape = BinaryTuringTape()
        elif isinstance(tape, list):
            self.tape = BinaryTuringTape(tape)
        else:
            self.tape = tape
        self.table = table
        self.state: TuringState = 0

    def read_tape(self) -> TuringSymbol:
        """Function version of `pointed_symbol`.

        Returns:
            TuringSymbols: Symbol read from tape
        """
        return self.tape.head_symbol

    def write_tape(self, value: TuringSymbol):
        """Function version of `pointed_symbol`.
        """
        self.tape.head_symbol = value

    @property
    def tape_tuple(self) -> TuringTapeTuple:
        """TuringTapeTuple of the Turing Machine. This represents current state.

        Returns:
            TuringTapeTuple: TuringTapeTuple of the machine
        """
        return TuringTapeTuple(
            state=self.state,
            left_number=self.tape.left_number,
            right_number=self.tape.right_number,
            head=self.tape.head_symbol
        )

    @tape_tuple.setter
    def tape_tuple(self, value: TuringTapeTuple):
        self.state = value.state
        self.tape = BinaryTuringTape.from_tape_tuple(value)

    def __str__(self) -> str:
        output_str = str(self.tape_tuple) + "\n"
        output_str += str(self.tape) + "\n"
        output_str += "state: " + str(self.state)
        return output_str

    def __next__(self):
        read = self.read_tape()
        transition: TuringTransition = self.table[self.state].transitions[0 if read ==
                                                                          TuringSymbol.ZERO else 1]
        self.write_tape(transition.write)
        self.tape.move_tape(transition.move)
        self.state = transition.next_state


if __name__ == "__main__":
    transition_table = TuringTransitionTable([TuringStateTransition(
        0,
        (
            TuringTransition(TuringSymbol.ONE, TuringDirection.RIGHT, 0),
            TuringTransition(TuringSymbol.ZERO, TuringDirection.RIGHT, 0)
        )
    )])
    test_tuple = TuringTapeTuple(
        0,
        7,
        6,
        TuringSymbol.ZERO,
    )
    test_tape = BinaryTuringTape.from_tape_tuple(test_tuple)
    print(test_tape)
    tape_init = [0, 1, 1, 1, 0, 0, 1, 1]
    machine = BinaryTuring(transition_table, tape_init)
    print(machine)
    for _ in range(10):
        next(machine)
    print(machine)
    machine.tape_tuple = test_tuple
    print(machine)
