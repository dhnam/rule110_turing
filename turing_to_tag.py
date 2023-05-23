"""From turing machine to tag system
"""

from binary_turing import TuringTransitionTable, TuringStateTransition, TuringTransition,\
    TuringSymbol, TuringDirection, BinaryTuring, BinaryTuringTape, TuringTapeTuple
from tag_system import TagSysTransition, TagSysTag, TagSysTape, TagSysSymbol, TagSystem


def turing_table_to_tag_transition(turing_table: TuringTransitionTable) -> TagSysTransition:
    """Make tag transition out of turing transition table

    Args:
        turing_table (TuringTransitionTable): source

    Returns:
        TagSysTransition: destination
    """
    tag_transition: TagSysTransition = {}
    for state_k in turing_table:
        transition = turing_table[state_k].transitions
        h_k: tuple[TagSysTag, TagSysTag] = ([], [])
        l_k: tuple[TagSysTag, TagSysTag] = ([], [])
        r_k: tuple[TagSysTag, TagSysTag] = ([], [])
        for z in (0, 1):  # pylint: disable=invalid-name
            if transition[z].move == TuringDirection.LEFT\
                    and transition[z].write == TuringSymbol.ONE:
                h_k[z].append(f"R_{transition[z].next_state}*")
                h_k[z].append(f"R_{transition[z].next_state}*")
            if z == 0:
                h_k[z].append(f"H_{transition[z].next_state}")
            h_k[z].append(f"H_{transition[z].next_state}")
            if transition[z].move == TuringDirection.RIGHT\
                    and transition[z].write == TuringSymbol.ONE:
                h_k[z].append(f"L_{transition[z].next_state}")
                h_k[z].append(f"L_{transition[z].next_state}")
            tag_transition[f"H_{state_k}:{z}"] = h_k[z]

            l_k[z].append(f"L_{transition[z].next_state}")
            if transition[z].move == TuringDirection.RIGHT:
                l_k[z].append(f"L_{transition[z].next_state}")
                l_k[z].append(f"L_{transition[z].next_state}")
                l_k[z].append(f"L_{transition[z].next_state}")
            tag_transition[f"L_{state_k}:{z}"] = l_k[z]

            r_k[z].append(f"R_{transition[z].next_state}")
            if transition[z].move == TuringDirection.LEFT:
                r_k[z].append(f"R_{transition[z].next_state}")
                r_k[z].append(f"R_{transition[z].next_state}")
                r_k[z].append(f"R_{transition[z].next_state}")
            tag_transition[f"R_{state_k}:{z}"] = r_k[z]
        tag_transition[f"R_{state_k}*"] = [f"R_{state_k}", f"R_{state_k}"]
        tag_transition[f"H_{state_k}"] = [f"H_{state_k}:1", f"H_{state_k}:0"]
        tag_transition[f"L_{state_k}"] = [f"L_{state_k}:1", f"L_{state_k}:0"]
        tag_transition[f"R_{state_k}"] = [f"R_{state_k}:1", f"R_{state_k}:0"]
    return tag_transition


def turing_machine_to_tag_tape(turing_machine: BinaryTuring) -> TagSysTape:
    """Make tag system tape out of current state of turing machine

    Args:
        turing_machine (BinaryTuring): Source

    Returns:
        TagSysTape: Destination
    """
    tape_state = turing_machine.tape_tuple
    tag_tape_list: list[TagSysSymbol] = [
        f"H_{tape_state.state}:1", f"H_{tape_state.state}:0"]
    for _ in range(tape_state.left_number):
        tag_tape_list += [f"L_{tape_state.state}:1", f"L_{tape_state.state}:0"]
    for _ in range(tape_state.right_number):
        tag_tape_list += [f"R_{tape_state.state}:1", f"R_{tape_state.state}:0"]

    if tape_state.head == TuringSymbol.ZERO:
        tag_tape_list = tag_tape_list[1:]

    return TagSysTape(tag_tape_list)


def turing_machine_to_tag_system(turing_machine: BinaryTuring) -> TagSystem:
    """Make tag system representing given turing machine

    Args:
        turing_machine (BinaryTuring): Source turing mahcine

    Returns:
        TagSystem: Tag system made
    """
    return TagSystem(
        turing_table_to_tag_transition(turing_machine.table),
        tape=turing_machine_to_tag_tape(turing_machine))


def is_step_passed(tag_sys: TagSystem) -> bool:
    """Check if one cycle of tag system is passed 

    Args:
        tag_sys (TagSystem): tag system to check

    Returns:
        bool: result
    """
    for next_symbol in tag_sys.tape.tape:
        if next_symbol[-2:] not in (":0", ":1"):
            return False
    return True


def tag_tape_to_turing_tape_tuple(tag_tape: TagSysTape) -> TuringTapeTuple:
    """Make turing tape tuple out of tag system tape.

    Args:
        tag_tape (TagSysTape): Tag tape, must be appropriate state.

    Returns:
        TuringTapeTuple: Calculated state of turing tape.
    """
    assert is_step_passed(tag_tape)
    tape = tag_tape.tape
    return TuringTapeTuple(
        state=int(tape[0][2:-2]),
        left_number=tape.count(f"L_{tape[0][2:-2]}:0"),
        right_number=tape.count(f"R_{tape[0][2:-2]}:0"),
        head=TuringSymbol.ONE if tape[0][-2:] == ":1" else TuringSymbol.ZERO,
    )


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
    example_tag = turing_machine_to_tag_system(example_turing_machine)
    print(tag_tape_to_turing_tape_tuple(example_tag.tape))
    next(example_turing_machine)
    next(example_tag)
    while not is_step_passed(example_tag):
        next(example_tag)
    print(example_turing_machine)
    print(tag_tape_to_turing_tape_tuple(example_tag.tape))
