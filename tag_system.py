"""Tag system. This is proven to be turing completed.
"""
TagSysSymbol = str
TagSysSymbolSet = set[TagSysSymbol]
TagSysTransition = dict[TagSysSymbol, list[TagSysSymbol]]


class TagSysTape:
    """Tape for Tag System
    """

    def __init__(self, tape: list[TagSysSymbol] | None = None):
        self.tape = []
        if tape is not None:
            self.tape = tape

    @property
    def head(self) -> TagSysSymbol:
        """First element of the tape.

        Returns:
            TagSysSymbol: Head element
        """
        return self.tape[0]

    def remove(self, num: int):
        """Remove first `num` entries from tape

        Args:
            num (int): Number of entries to remove
        """
        self.tape = self.tape[num:]

    def tag(self, symbols: list[TagSysSymbol]):
        """Tag the tape with given symbols

        Args:
            symbols (list[TagSysSymbol]): Symbols to tag with
        """
        self.tape.extend(symbols)

    def __str__(self):
        return str(self.tape)


class TagSystem:
    """Tag System
    """

    def __init__(
        self,
        transition: TagSysTransition,
        num: int = 2,
        tape: TagSysTape | list[TagSysSymbol] | None = None,
    ):
        self.tape: TagSysTape
        self.transition = transition
        if isinstance(tape, TagSysTape):
            self.tape = tape
        else:
            self.tape = TagSysTape(tape)
        self.num = num

    @property
    def symbol_set(self) -> TagSysSymbolSet:
        """Symbol set of the system. Read only. Based on transition table.

        Returns:
            TagSysSymbolSet: Set of symbols
        """
        return set(self.transition)

    def __next__(self):
        try:
            self.tape.tag(self.transition[self.tape.head])
        except KeyError as err:
            raise StopIteration from err
        self.tape.remove(self.num)
        return self

    def __iter__(self):
        return self

    def __str__(self):
        return str(self.tape)


if __name__ == "__main__":
    transition_table: TagSysTransition = {
        "a": ["b", "c"],
        "b": ["a"],
        "c": ["a", "a", "a", "a"],
    }

    tag_machine = TagSystem(transition_table, tape=["a", "a", "a"])
    print(tag_machine)

    for _ in range(5):
        next(tag_machine)
        print(tag_machine)
