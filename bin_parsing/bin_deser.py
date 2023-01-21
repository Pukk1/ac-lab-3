from isa import Instruction, OpcodeOperandsType, Opcode
from utils import bin_to_number


def get_opcode(instr: str) -> Opcode:
    opcode_bin: str = instr[-4:]
    opcode_number: int = bin_to_number(opcode_bin, False)
    for opcode in Opcode:
        if opcode.value.code == opcode_number:
            return opcode
    assert False, 'Opcode not found for opcode_bin: ' + opcode_bin


def get_operands_type(instr: str) -> OpcodeOperandsType:
    type_bin: str = instr[-8:][:3]
    type_number: int = bin_to_number(type_bin, False)
    for op_type in OpcodeOperandsType:
        if op_type.value == type_number:
            return op_type
    assert False, 'Opcode operands type not found for: ' + type_bin


def get_operands(instr: str, operand_type: OpcodeOperandsType) -> list[int]:
    bin_operands_str: str = instr[:-8]
    operands: list[int] = []
    if operand_type == OpcodeOperandsType.NONE:
        return operands
    elif operand_type == OpcodeOperandsType.CONST:
        operands.append(bin_to_number(bin_operands_str[:16], True))
    elif operand_type == OpcodeOperandsType.REG_CONST:
        reg_const: str = bin_operands_str[:20]
        operands.append(bin_to_number(reg_const[:4], False))
        operands.append(bin_to_number(reg_const[-16:], True))
    elif operand_type == OpcodeOperandsType.REG_REG_REG:
        reg_reg_reg: str = bin_operands_str[:12]
        operands.append(bin_to_number(reg_reg_reg[:4], False))
        operands.append(bin_to_number(reg_reg_reg[-8:][:4], False))
        operands.append(bin_to_number(reg_reg_reg[-4:], False))
    elif operand_type == OpcodeOperandsType.REG_REG_CONST:
        reg_reg_const: str = bin_operands_str[:24]
        operands.append(bin_to_number(reg_reg_const[:4], False))
        operands.append(bin_to_number(reg_reg_const[-20:][:4], False))
        operands.append(bin_to_number(reg_reg_const[-16:], True))
    elif operand_type == OpcodeOperandsType.REG_REG:
        reg_reg: str = bin_operands_str[:8]
        operands.append(bin_to_number(reg_reg[:4], False))
        operands.append(bin_to_number(reg_reg[-4:], False))
    elif operand_type == OpcodeOperandsType.REG:
        operands.append(bin_to_number(bin_operands_str[:4], False))
    else:
        assert False, 'Can\'t parse operands from bin for instr: ' + instr

    return operands


def deserialize_instr(instr: str) -> Instruction:
    opcode: Opcode = get_opcode(instr)
    operands_type: OpcodeOperandsType = get_operands_type(instr)
    operands: list[int] = get_operands(instr, operands_type)
    return Instruction(opcode, operands_type, operands)


def deserialize_bin(bin_lines: list[str]) -> tuple[list[int], list[Instruction]]:
    number_of_data_lines: int = bin_to_number(bin_lines[0], False)
    init_data: list[int] = []
    instructions: list[Instruction] = []
    for i in range(1, number_of_data_lines + 1):
        init_data.append(bin_to_number(bin_lines[i], True))

    bin_lines = bin_lines[number_of_data_lines + 1:]
    for bin_line in bin_lines:
        instr: Instruction = deserialize_instr(bin_line)
        instructions.append(instr)

    return init_data, instructions
