from tag_system import TagSysTransition, TagSysTag, TagSysTape, TagSysSymbol, TagSystem
from cyclic_tag import CyclicTransition, CyclicTag, CyclicSymbol, CyclicTagSystem, CyclicTape

def tag_system_to_cyclic_tags_dict(tag_system: TagSystem) -> dict[TagSysSymbol, CyclicTag]:
    tags = tag_system.symbol_set
    tag_count = len(tags)
    tag_dict: dict[TagSysSymbol, CyclicTag] = {}
    for i, next_tag in enumerate(tags):
        tag_dict[next_tag] = CyclicTag.fromstr("0" * i + "1" + "0" * (tag_count - i - 1))
    return tag_dict

def tag_system_to_cyclic_transitions(tag_system: TagSystem, num:int=2) -> CyclicTransition:
    trans_dict = tag_system_to_cyclic_tags_dict(tag_system)
    transition: list[CyclicTag] = []
    for next_cyclic_symbol in trans_dict:
        next_tag: list[CyclicSymbol] = []
        for next_tag_symbol in tag_system.transition[next_cyclic_symbol]:
            next_tag.extend(trans_dict[next_tag_symbol])
        transition.append(CyclicTag(next_tag))
    for _ in range(len(trans_dict) * (num - 1)):
        transition.append("")
    return CyclicTransition(transition)

def tag_system_to_cyclic_tape(tag_system: TagSystem) -> CyclicTape:
    tape: list[CyclicSymbol] = []
    trans_dict = tag_system_to_cyclic_tags_dict(tag_system)
    for next_symbol in tag_system.tape.tape:
        tape.extend(trans_dict[next_symbol])
    return CyclicTape(tape)

def cyclic_tape_to_tag_tape(cyclic_tape: CyclicTape, trans_dict: dict[TagSysSymbol, CyclicTag]) -> TagSysTape:
    assert len(cyclic_tape.tape) % len(trans_dict) == 0
    # https://docs.python.org/3/library/itertools.html#itertools-recipes grouper
    args = [iter(cyclic_tape.tape)] * len(trans_dict)
    for next_chunk in zip(*args):
        print(next_chunk)
    
if __name__ == "__main__":
    transition_table: TagSysTransition = {
        "a": ["b", "c"],
        "b": ["a"],
        "c": ["a", "a", "a", "a"],
    }

    tag_machine = TagSystem(transition_table, tape=["a", "a", "a"])
    print(tag_machine)
    print(dict := tag_system_to_cyclic_tags_dict(tag_machine))
    print(cyclic_transition := tag_system_to_cyclic_transitions(tag_machine))
    print(tape := tag_system_to_cyclic_tape(tag_machine))
    cyclic_machine = CyclicTagSystem(cyclic_transition, tape)
    for _ in range(6):
        next(cyclic_machine)
        print(cyclic_machine)
    next(tag_machine)
    print(tag_machine)
    cyclic_tape_to_tag_tape(cyclic_machine.tape, dict)