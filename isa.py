"""файл со структурами предназначенными для описания команд, типов их наборов аргументов в структурном виде"""

from enum import Enum


class OpcodeOperandsType(int, Enum):
    """тип набора аргументов инструкции"""
    # машинное слово 32 бита
    # 0-3 бит под код opcode
    # 4-й бит под специфику команды (вид адрессации например)
    # 5-7 бит под тип набора операндов

    # 8-31 бит пустые
    NONE = 0b000
    # 8-11 бит пустые (либо под расширение специфики команды), 12-15 пустые, 16-31 бит заняты константой
    CONST = 0b001
    # 8-11 бит пустые (либо под расширение специфики команды), 12-27 бит константа, 28-31 бит регистр
    REG_CONST = 0b010
    # 8-19 пустые, 20-23 бит под регистр, 24-27 бит под регистр, 28-31 бит под регистр
    REG_REG_REG = 0b011
    # 8-23 бит под константу, 24-27 бит под регистр, 28-31 бит под регистр
    REG_REG_CONST = 0b100
    # 8-23 бит пустые, 24-27 бит под регистр, 28-31 бит под регистр
    REG_REG = 0b101
    # 8-27 бит пустые, 28-31 бит под регистр
    REG = 0b110
    # REG_CONST_REG = 0b111


class OpcodeInfo:
    """информация о типе инструкции: бинарный код, возможные наборы аргументов"""

    def __init__(self, code: int, available_types: list[OpcodeOperandsType]):
        self.code: int = code
        self.available_types: list[OpcodeOperandsType] = available_types


class Opcode(Enum):
    """возможные типы инструкций"""
    HLT = OpcodeInfo(0b0000, [OpcodeOperandsType.NONE])
    ADD = OpcodeInfo(0b0001, [OpcodeOperandsType.REG_REG_CONST, OpcodeOperandsType.REG_REG_REG])
    SUB = OpcodeInfo(0b0010, [OpcodeOperandsType.REG_REG_CONST, OpcodeOperandsType.REG_REG_REG])
    MUL = OpcodeInfo(0b0011, [OpcodeOperandsType.REG_REG_CONST, OpcodeOperandsType.REG_REG_REG])
    DIV = OpcodeInfo(0b0100, [OpcodeOperandsType.REG_REG_CONST, OpcodeOperandsType.REG_REG_REG])
    MOD = OpcodeInfo(0b0101, [OpcodeOperandsType.REG_REG_CONST, OpcodeOperandsType.REG_REG_REG])
    JMP = OpcodeInfo(0b0110, [OpcodeOperandsType.CONST])
    BEQ = OpcodeInfo(0b0111, [OpcodeOperandsType.CONST])
    BNE = OpcodeInfo(0b1000, [OpcodeOperandsType.CONST])
    LD = OpcodeInfo(0b1001, [OpcodeOperandsType.REG_CONST])
    ST = OpcodeInfo(0b1010, [OpcodeOperandsType.REG_CONST])
    PRINT = OpcodeInfo(0b1011, [OpcodeOperandsType.REG])
    READ = OpcodeInfo(0b1100, [OpcodeOperandsType.REG])


class Instruction:
    """структурное представление инструкции"""

    def __init__(self, opcode: Opcode, operands_type: OpcodeOperandsType, operands: list[int]):
        self.opcode: Opcode = opcode
        self.operands_type: OpcodeOperandsType = operands_type
        self.operands: list[int] = operands

    def __repr__(self):
        operands: list[str] = list(map(lambda it: str(it), self.operands))
        return "opcode={} operands_type={} operands={}".format(self.opcode.name, self.operands_type.name, operands)
