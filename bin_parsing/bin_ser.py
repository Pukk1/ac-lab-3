from isa import Instruction, OpcodeOperandsType
from translate.translation_regex import is_section_instr, get_section_name, is_comment_or_label, is_word_instr, \
    get_word_value
from utils import number_to_bin


def create_init_bin_data(code_lines: list[str]) -> list[str]:
    bin_data: list[str] = []
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

    return bin_data


def create_bin_instructions(instructions: list[Instruction]) -> list[str]:
    bin_instructions: list[str] = []
    for instruction in instructions:
        bin_instruction = number_to_bin(instruction.opcode.value.code, 4)
        bin_instruction = '0' + bin_instruction  # для упрощения у команд была убрана их специфика
        bin_instruction = number_to_bin(instruction.operands_type.value, 3) + bin_instruction
        bin_instruction = bin_args_by_type(instruction.operands, instruction.operands_type) + bin_instruction
        bin_instructions.append(bin_instruction)
    return bin_instructions


def bin_args_by_type(args: list[int], op_type: OpcodeOperandsType) -> str:
    if op_type == OpcodeOperandsType.NONE:
        return number_to_bin(0, 24)
    elif op_type == OpcodeOperandsType.CONST:
        return number_to_bin(args.pop(0), 16) + '0000' + '0000'
    elif op_type == OpcodeOperandsType.REG_CONST:
        return number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 16) + '0000'
    elif op_type == OpcodeOperandsType.REG_REG_REG:
        return number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4) \
            + number_to_bin(args.pop(0), 4) + number_to_bin(0, 12)
    elif op_type == OpcodeOperandsType.REG_REG_CONST:
        return number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 16)
    elif op_type == OpcodeOperandsType.REG:
        return number_to_bin(args.pop(0), 4) + number_to_bin(0, 20)
    elif op_type == OpcodeOperandsType.REG_REG:
        return number_to_bin(args.pop(0), 4) + number_to_bin(args.pop(0), 4)
    else:
        assert False, 'Can\'t cast args: ' + str(args) + ' opcode_typed: ' + str(op_type.name)
