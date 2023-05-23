from tag_system import TagSysTransition, TagSysTag, TagSysTape, TagSysSymbol, TagSystem
from cyclic_tag import CyclicTransition, CyclicTag, CyclicSymbol, CyclicTagSystem, CyclicTape

TagToCyclicTranslationDict = dict[TagSysSymbol, CyclicTag]

def tag_system_to_cyclic_tags_dict(tag_system: TagSystem) -> TagToCyclicTranslationDict:
    tags = tag_system.symbol_list
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

def cyclic_tape_dict_to_tag_tape(cyclic_tape: CyclicTape, trans_dict: TagToCyclicTranslationDict) -> TagSysTape:
    assert len(cyclic_tape.tape) % len(trans_dict) == 0
    # https://docs.python.org/3/library/itertools.html#itertools-recipes grouper
    args = [iter(cyclic_tape.tape)] * len(trans_dict)
    reverse_trans_dict = {}
    for key, value in trans_dict.items():
        assert value not in reverse_trans_dict
        reverse_trans_dict[value] = key
    tag_tape_list = []
    for next_chunk in zip(*args):
        tag_tape_list += reverse_trans_dict[CyclicTag(next_chunk)]
    return TagSysTape(tag_tape_list)

def cyclic_transition_to_symbol_count(cyclic_transition: CyclicTransition) -> int:
    return len([s for s in cyclic_transition.transitions if len(s) == 0])

def cyclic_transition_dict_to_tag_transition(cyclic_transition: CyclicTransition, trans_dict:TagToCyclicTranslationDict) -> TagSysTransition:
    reverse_trans_dict: dict[CyclicTag, TagSysSymbol] = {}
    for key, value in trans_dict.items():
        assert value not in reverse_trans_dict
        reverse_trans_dict[value] = key
    symbol_count = cyclic_transition_to_symbol_count(cyclic_transition)
    tag_trans:TagSysTransition = {}
    for i, next_transition_tag in enumerate(cyclic_transition):
        if len(next_transition_tag) == 0:
            break
        ith_tag = CyclicTag(CyclicSymbol.YES if idx==i else CyclicSymbol.NO for idx in range(symbol_count))
        args = [iter(next_transition_tag)] * len(trans_dict)
        next_tag_sys_tag: TagSysTag = TagSysTag()
        for next_chunk in zip(*args):
            next_cyclic_tag = CyclicTag(next_chunk)
            next_tag_sys_tag.append(reverse_trans_dict[next_cyclic_tag])
            
        tag_trans[reverse_trans_dict[ith_tag]] = next_tag_sys_tag
    return tag_trans

def cyclic_system_dict_to_tag_system(cyclic_system: CyclicTagSystem, trans_dict: TagToCyclicTranslationDict) -> TagSystem:
    c_tape = cyclic_system.tape
    c_transition = cyclic_system.transition
    t_tape = cyclic_tape_dict_to_tag_tape(c_tape, trans_dict)
    t_transition = cyclic_transition_dict_to_tag_transition(c_transition, trans_dict)
    num, mod = divmod(len(cyclic_transition), cyclic_transition_to_symbol_count(c_transition))
    assert mod == 0
    return TagSystem(t_transition, num, t_tape)

def is_tag_step_passed(cyclic: CyclicTagSystem) -> bool:
    return cyclic.transition.point == 0

def tag_system_to_cyclic_machine(tag_machine:TagSystem) -> CyclicTagSystem:
    return CyclicTagSystem(tag_system_to_cyclic_transitions(tag_machine), tag_system_to_cyclic_tape(tag_machine))
    
if __name__ == "__main__":
    transition_table: TagSysTransition = {
        "a": ["b", "c"],
        "b": ["a"],
        "c": ["a", "a", "a", "a"],
    }

    tag_machine = TagSystem(transition_table, tape=["a", "a", "a"])
    print(tag_machine)
    print(tag_dict := tag_system_to_cyclic_tags_dict(tag_machine))
    print(cyclic_transition := tag_system_to_cyclic_transitions(tag_machine))
    print(tape := tag_system_to_cyclic_tape(tag_machine))
    cyclic_machine = CyclicTagSystem(cyclic_transition, tape)
    next(cyclic_machine)
    print(cyclic_machine)
    while not is_tag_step_passed(cyclic_machine):
        next(cyclic_machine)
        print(cyclic_machine)
    next(tag_machine)
    print(tag_machine)
    print(cyclic_system_dict_to_tag_system(cyclic_machine, tag_dict))