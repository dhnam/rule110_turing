"""Cyclic Tag System.
This is simpler version of tag system thus turing complete.
"""
from __future__ import annotations
from enum import Enum


class CyclicSymbol(Enum):
    """Symbol of Cyclic system
    """
    NO = 0
    YES = 1


class CyclicTag(list[CyclicSymbol]):
    """Custom list of Cyclic Symbol
    """
    def __str__(self):
        return " ".join("0" if x == CyclicSymbol.NO else "1" for x in self)
    @staticmethod
    def fromstr(string: str) -> CyclicTag:
        """Get list of CyclicSymbol from string of 0 and 1s.

        Args:
            string (str): String consisted with 0 and 1

        Returns:
            CyclicTag: list of Cyclic Symbol
        """
        return CyclicTag(CyclicSymbol.NO if x == "0" else CyclicSymbol.YES for x in string)


class CyclicTransition:
    """Transition table of Cyclic Tag System
    """

    def __init__(self, transition_list: list[CyclicTag]):
        self.transitions = transition_list
        self.point = 0

    def __iter__(self):
        return self

    def __next__(self) -> CyclicTag:
        val = self.transitions[self.point]
        self.point += 1
        if self.point >= len(self.transitions):
            self.point = 0
        return val

    def __str__(self):
        string = ""
        for i, next_transition in enumerate(self.transitions):
            string += f"{i}: {next_transition}"
            if i == self.point:
                string += " <<<"
            string += "\n"
        string = string[:-1]
        return string


class CyclicTape:
    """Tape for Cyclic Tag System
    """

    def __init__(self, tape: list[CyclicSymbol] | None = None):
        self.tape = []
        if tape is not None:
            self.tape = tape

    def pop(self) -> CyclicSymbol:
        """Remove first element of the tape and returns.

        Returns:
            CyclicSymbol: Head element
        """
        return self.tape.pop(0)

    def tag(self, symbols: CyclicTag):
        """Tag the tape with given symbols

        Args:
            symbols (CyclicTag): Symbols to tag with
        """
        self.tape.extend(symbols)

    def __str__(self):
        string = ""
        for next_symbol in self.tape:
            if next_symbol == CyclicSymbol.YES:
                string += "1 "
            else:
                string += "0 "
        return string


class CyclicTagSystem:
    """Cyclic Tag System
    """

    def __init__(self, transition: CyclicTransition, tape: CyclicTape | list[CyclicSymbol | int] | None = None):
        self.transition = transition
        self.tape: CyclicTape
        if isinstance(tape, CyclicTape):
            self.tape = tape
        else:
            self.tape = CyclicTape(tape)

    def __next__(self):
        next_symbol = self.tape.pop()
        next_tag = next(self.transition)
        if next_symbol == CyclicSymbol.YES:
            self.tape.tag(next_tag)

    def __str__(self):
        string = str(self.tape) + "\n"
        string += "==============\n"
        string += str(self.transition) + "\n"
        string += "=============="
        return string


if __name__ == "__main__":
    exampleTape = CyclicTape(CyclicTag.fromstr("011011101"))
    exampleTransition = CyclicTransition([
        CyclicTag.fromstr("11"),
        CyclicTag.fromstr("0011"),
        CyclicTag.fromstr("1101"),
    ])
    exampleSystem = CyclicTagSystem(exampleTransition, exampleTape)

    print(exampleSystem)
    next(exampleSystem)
    print(exampleSystem)
    next(exampleSystem)
    print(exampleSystem)
    next(exampleSystem)
    print(exampleSystem)
    next(exampleSystem)
