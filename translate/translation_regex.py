import re

from isa import Opcode, OpcodeOperandsType

OPCODE_OPERAND_TYPE_VIEW: dict = {
    OpcodeOperandsType.NONE: r'^$',
    OpcodeOperandsType.CONST: r'^-?[0-9]+$',
    OpcodeOperandsType.REG: r'^reg[0-4]$',
    OpcodeOperandsType.REG_REG: r'^reg[0-4]\s*,\s*reg[0-4]$',
    OpcodeOperandsType.REG_CONST: r'^reg[0-4]\s*,\s*-?[0-9]+$',
    OpcodeOperandsType.REG_REG_REG: r'^reg[0-4]\s*,\s*reg[0-4]\s*,\s*reg[0-4]$',
    OpcodeOperandsType.REG_REG_CONST: r'^reg[0-4]\s*,\s*reg[0-4]\s*,\s*-?[0-9]+$'
}


def is_section_instr(instr: str) -> bool:
    return re.match(r'^section\s+\.[a-z]+$', instr) is not None


def get_section_name(instr: str) -> str:
    return instr.split('.')[1]


def is_label_instr(instr: str) -> bool:
    return re.match(r'^[a-z]+:$', instr) is not None


def is_word_instr(instr: str) -> bool:
    return re.match(r'^word\s+-?[0-9]+$', instr) is not None


def get_word_value(instr: str) -> str:
    return re.findall(r'(-?[0-9]+)', instr).pop(0)


def is_comment_instr(instr: str) -> bool:
    return re.match(r'^#', instr) is not None


def is_comment_or_label(instr: str):
    return is_comment_instr(instr) or is_label_instr(instr)


def get_opcode_regex(opcode: Opcode) -> re:
    return r'^' + opcode.name.lower()
