"""модуль занимается преобразованием операций из section .text и данных из section .data в набор бинарных инструкций"""

from src.isa import Instruction, OpcodeOperandsType
from src.translate.translation_regex import is_section_instr, get_section_name, is_comment_or_label, is_word_instr, \
    get_word_value
from src.utils import number_to_bin, bin_to_number


def create_init_bin_data(code_lines: list[str]) -> tuple[list[str], list[str]]:
    """создать бинарное представление section .data"""
    bin_data: list[str] = []
    data_mnemonics: list[str] = []
    current_section: str = ''
    for line in code_lines:
        if is_section_instr(line):
            current_section = get_section_name(line)
            continue

        if current_section == 'data':
            if is_comment_or_label(line):
                continue
            if is_word_instr(line):
                value: int = int(get_word_value(line))

                assert -pow(2, 31) <= value < pow(2, 31), \
                    'Value=' + str(value) + ' not in interval: ' + str(-pow(2, 31)) + '..' + str(pow(2, 31))

                bin_data.append(number_to_bin(value, 32))
                data_mnemonics.append(str(value))

    return bin_data, data_mnemonics


def bin_args_by_type(args: list[int], op_type: OpcodeOperandsType) -> str:
    """преобразовать набор аргументов в бинарные вид, в соответствии с типом набора аргументов"""
    bin_args: str
    if op_type == OpcodeOperandsType.NONE:
        bin_args = number_to_bin(0, 24)
    elif op_type == OpcodeOperandsType.CONST:
        bin_args = number_to_bin(args.pop(0), 16) + '0000' + '0000'
    elif op_type == OpcodeOperandsType.REG_CONST:
        bin_args = number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 16) + '0000'
    elif op_type == OpcodeOperandsType.REG_REG_REG:
        bin_args = number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0),
                                                                                                 4) + number_to_bin(0,
                                                                                                                    12)
    elif op_type == OpcodeOperandsType.REG_REG_CONST:
        bin_args = number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 16)
    elif op_type == OpcodeOperandsType.REG:
        bin_args = number_to_bin(args.pop(0), 4) + number_to_bin(0, 20)
    elif op_type == OpcodeOperandsType.REG_REG:
        bin_args = number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4)
    else:
        assert False, 'Can\'t cast args: ' + str(args) + ' opcode_typed: ' + str(op_type.name)
    return bin_args


def create_bin_instructions(instructions: list[Instruction]) -> tuple[list[str], list[Instruction]]:
    """создать бинарное представление инструкции и набора её аргументов"""
    bin_instructions: list[str] = []
    for instruction in instructions:
        bin_instruction = number_to_bin(instruction.opcode.value.code, 4)
        bin_instruction = '0' + bin_instruction  # для упрощения у команд была убрана их специфика
        bin_instruction = number_to_bin(instruction.operands_type.value, 3) + bin_instruction
        bin_instruction = bin_args_by_type(instruction.operands.copy(), instruction.operands_type) + bin_instruction
        bin_instructions.append(bin_instruction)
    return bin_instructions, instructions


def binline_to_ascii_code(line: str):
    result = ''
    for i in range(0, 32, 8):
        code = line[:8]
        code = bin_to_number(code, False)
        result += chr(code)
        line = line[8:]
    return result
