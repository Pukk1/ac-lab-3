#!/usr/bin_parsing/python3
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=consider-using-f-string
# pylint: disable=import-error
# pylint: disable=too-few-public-methods
"""Модель процессора, позволяющая выполнить странслированные программы на языке Assembler."""

import logging
import sys
from typing import Optional

from src.bin_parsing.bin_deser import deserialize_bin_lines_list, ascii_code_to_binline
from src.isa import Instruction, OpcodeOperandsType, Opcode
from src.utils import read_bin_code_from_file, read_char_list_from_file


class Alu:
    """структурное представление физического АЛУ"""

    def __init__(self):
        self.op2: int = 0
        self.op1: int = 0
        self.res: int = 0
        self.zero: bool = False
        self.operations: dict = {
            Opcode.ADD: lambda left, right: left + right,
            Opcode.SUB: lambda left, right: left - right,
            Opcode.MUL: lambda left, right: left * right,
            Opcode.DIV: lambda left, right: int(left / right),
            Opcode.MOD: lambda left, right: left % right,
        }

    def execute(self, opcode: Opcode):
        """выполнение выбранной арифметической операции с использованием op1 и op2,
        результат записывается в res (физически передаётся на шину результата АЛУ)"""
        self.res = self.operations[opcode](self.op1, self.op2)

        while self.res > pow(2, 31) - 1:
            self.res -= 2 * pow(2, 31)
        while self.res < -pow(2, 31):
            self.res += 2 * pow(2, 31)

        if self.res == 0:
            self.zero = True
        else:
            self.zero = False


class RegFile:
    """структурное представление физического регистрового файла.
    Внутри _valued_regs не хранится нулевой регистр,
    его логика раборы расписана отдельно в методах choice_ops и set_reg_value тк он константно равен нулю"""

    def __init__(self):
        self.op1: int = 0
        self.op2: int = 0
        self._valued_regs: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}

    def choice_ops(self, op1_reg_num: int, op2_reg_num: int):
        if op1_reg_num == 0:
            self.op1 = 0
        else:

            self.op1 = self._valued_regs[op1_reg_num]
        if op2_reg_num == 0:
            self.op2 = 0
        else:

            self.op2 = self._valued_regs[op2_reg_num]

    def set_reg_value(self, reg_num: int, value: int):
        if reg_num != 0:
            self._valued_regs[reg_num] = value

    def get_all_regs(self) -> dict[int, int]:
        return self._valued_regs


class DataMem:
    """структурное представление физической памяти данных"""

    def __init__(self, data_memory_size: int, init_data: list[int]):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.mem: list[int] = [0] * data_memory_size
        self.res: int = 0
        self.input_connect_address: int = data_memory_size - 2
        self.output_connect_address: int = data_memory_size - 1

        for i, number in enumerate(init_data):
            self.mem[i] = number


class DataPath:
    """структурное представление физического модуля процессора DataPath.
    Содержит методы для работы между устройствами находящимися внутри модуля: Alu, DataMem, RegFile"""

    def __init__(self, data_memory_size: int, init_data: list[int], input_buffer: list[int]):
        self._input_buffer: list[int] = input_buffer
        self._output_buffer: list[int] = []
        self.data_mem: DataMem = DataMem(data_memory_size, init_data)
        self.alu: Alu = Alu()
        self.reg_file: RegFile = RegFile()

    def latch_res(self, res_reg_num: int, sig_read_data: bool):
        if sig_read_data:
            data = self.data_mem.res
        else:
            data = self.alu.res
        self.reg_file.set_reg_value(res_reg_num, data)

    def mem_read(self):
        if self.alu.res == self.data_mem.input_connect_address:
            try:
                self.data_mem.res = int(self._input_buffer.pop(0))
            except IndexError as data_empty_except:
                raise EOFError() from data_empty_except
        else:
            self.data_mem.res = self.data_mem.mem[self.alu.res]

    def mem_write(self):
        self.data_mem.mem[self.alu.res] = self.reg_file.op2
        if self.alu.res == self.data_mem.output_connect_address:
            self._output_buffer.append(self.data_mem.mem[self.alu.res])

    def get_output_buffer(self) -> list[int]:
        return self._output_buffer


class ControlUnit:
    """структурное представление физического модуля ControlUnit.
    Содержит методы для работы между устройствами находящимися внутри модуля: PC, DataPath,
    const (константное значение подаваемое из control unit на алу).
    Устанавливает взаимодействие между памятью инструкций и памятью данных (Гарвардская архитектура).
    Посылает сигналы для работы устройств, входящих в модуль,
    а так же мультиплексоров, обеспечивающих их взаимодействие"""

    def __init__(self, instructions: list[Instruction], data_path: DataPath):
        self.tick_counter: int = 0
        self.instructions: list[Instruction] = instructions
        self.program_counter: int = 0
        self.data_path: DataPath = data_path
        self.const: int = 0

    def tick(self) -> None:
        self.tick_counter += 1

    def latch_program_counter(self, sig_next: bool) -> None:
        if sig_next:
            self.program_counter += 1
        else:
            self.program_counter = self.data_path.alu.res

    def latch_exec_alu(self, sig_const: bool, opcode: Opcode) -> None:
        """выполнение операции на АЛУ и подача результата операции на шину результата"""
        self.data_path.alu.op1 = self.data_path.reg_file.op1
        if sig_const:
            self.data_path.alu.op2 = self.const
        else:
            self.data_path.alu.op2 = self.data_path.reg_file.op2
        self.data_path.alu.execute(opcode)

    # ==================================================================================================================
    # выполнение операций в виде отдельных функций, с расчетом затрачиваемого количества тактов процессора =============
    def exec_jmp(self, offset: int):
        self.const = self.program_counter + offset
        self.data_path.reg_file.choice_ops(0, 0)
        self.latch_exec_alu(True, Opcode.ADD)
        self.latch_program_counter(sig_next=False)
        self.tick()

    def exec_beq(self, offset: int):
        if self.data_path.alu.zero:
            self.exec_jmp(offset)
        else:
            self.latch_program_counter(sig_next=True)
            self.tick()

    def exec_bne(self, offset: int):
        if not self.data_path.alu.zero:
            self.exec_jmp(offset)
        else:
            self.latch_program_counter(sig_next=True)
            self.tick()

    def exec_st(self, reg_num: int, data_mem_address: int):
        self.const = data_mem_address
        self.data_path.reg_file.choice_ops(0, reg_num)
        self.latch_exec_alu(sig_const=True, opcode=Opcode.ADD)
        self.data_path.mem_write()
        self.latch_program_counter(sig_next=True)
        self.tick()

    def exec_ld(self, reg_num: int, data_mem_address: int):
        self.const = data_mem_address
        self.data_path.reg_file.choice_ops(0, 0)
        self.latch_exec_alu(sig_const=True, opcode=Opcode.ADD)
        self.data_path.mem_read()
        self.tick()
        self.data_path.latch_res(reg_num, sig_read_data=True)
        self.latch_program_counter(sig_next=True)
        self.tick()

    def exec_print(self, reg_num: int):
        self.exec_st(reg_num, self.data_path.data_mem.output_connect_address)

    def exec_read(self, reg_num: int):
        self.exec_ld(reg_num, self.data_path.data_mem.input_connect_address)

    def exec_alu_instr_with_const(self, opcode: Opcode, res_reg_num: int, arg_reg_num: int, const_arg: int):
        self.const = const_arg
        self.data_path.reg_file.choice_ops(arg_reg_num, 0)
        self.latch_exec_alu(sig_const=True, opcode=opcode)
        self.data_path.latch_res(res_reg_num, sig_read_data=False)
        self.latch_program_counter(sig_next=True)
        self.tick()

    def exec_alu_instr_with_reg(self, opcode: Opcode, res_reg_num: int, first_arg_reg_num: int,
                                second_arg_reg_num: int):
        self.data_path.reg_file.choice_ops(first_arg_reg_num, second_arg_reg_num)
        self.latch_exec_alu(sig_const=False, opcode=opcode)
        self.data_path.latch_res(res_reg_num, sig_read_data=False)
        self.latch_program_counter(sig_next=True)
        self.tick()

    # ==================================================================================================================

    def execute_instruction(self):
        """функция для последовательного выполнения инструкций из instr_mem"""
        instruction: Instruction = self.instructions[self.program_counter]
        opcode: Opcode = instruction.opcode

        if opcode is Opcode.HLT:
            raise StopIteration()

        if opcode is Opcode.JMP:
            offset: int = instruction.operands[0]
            self.exec_jmp(offset)
        elif opcode is Opcode.BEQ:
            offset: int = instruction.operands[0]
            self.exec_beq(offset)
        elif opcode is Opcode.BNE:
            offset: int = instruction.operands[0]
            self.exec_bne(offset)
        elif opcode is Opcode.LD:
            reg_num: int = instruction.operands[0]
            data_mem_addr: int = instruction.operands[1]
            self.exec_ld(reg_num, data_mem_addr)
        elif opcode is Opcode.ST:
            reg_num: int = instruction.operands[0]
            data_mem_addr: int = instruction.operands[1]
            self.exec_st(reg_num, data_mem_addr)
        elif opcode is Opcode.PRINT:
            reg_num: int = instruction.operands[0]
            self.exec_print(reg_num)
        elif opcode is Opcode.READ:
            reg_num: int = instruction.operands[0]
            self.exec_read(reg_num)
        else:
            if instruction.operands_type is OpcodeOperandsType.REG_REG_CONST:
                opcode: Opcode = instruction.opcode
                res_reg_num: int = instruction.operands[0]
                arg_reg_num: int = instruction.operands[1]
                const_arg: int = instruction.operands[2]
                self.exec_alu_instr_with_const(opcode, res_reg_num, arg_reg_num, const_arg)
            else:
                opcode: Opcode = instruction.opcode
                res_reg_num: int = instruction.operands[0]
                first_arg_reg_num: int = instruction.operands[1]
                second_arg_reg_num: int = instruction.operands[2]
                self.exec_alu_instr_with_reg(opcode, res_reg_num, first_arg_reg_num, second_arg_reg_num)

    def __repr__(self):
        alu_data_mem: Optional[int] = None
        if 0 <= self.data_path.alu.res < len(self.data_path.data_mem.mem):
            alu_data_mem = self.data_path.data_mem.mem[self.data_path.alu.res]

        state = "{{TICK: {}, PC: {}, ALU_RES: {}, DATA_MEM[ALU_RES]: {}, REG1: {}, REG2: {}, REG3: {}, REG4: {}}}".format(
            self.tick_counter,
            self.program_counter,
            self.data_path.alu.res,
            alu_data_mem,
            self.data_path.reg_file.get_all_regs()[1],
            self.data_path.reg_file.get_all_regs()[2],
            self.data_path.reg_file.get_all_regs()[3],
            self.data_path.reg_file.get_all_regs()[4]
        )

        instr = self.instructions[self.program_counter]
        opcode = instr.opcode
        args_type: OpcodeOperandsType = instr.operands_type
        args = instr.operands
        action = "{} {} {}".format(opcode.name, args_type.name, str(args))

        return "{} {}".format(action, state)


def get_output_line(output_buff: list[int], print_char: bool) -> str:
    output: str = ''
    for it in output_buff:
        if print_char and 0 <= it < 256:
            output += chr(it)
        else:
            output += str(it)
    return output


def simulation(init_data: list[int], instructions: list[Instruction],
               input_tokens: list[int], data_memory_size: int, limit: int) -> tuple[str, int, int]:
    """запуск симуляции работы процессора"""

    data_path = DataPath(data_memory_size, init_data, input_tokens)
    control_unit = ControlUnit(instructions, data_path)
    instr_counter = 0

    try:
        while True:
            assert limit > instr_counter, "Too long execution, increase limit!"
            logging.debug('%s', control_unit)
            control_unit.execute_instruction()
            instr_counter += 1
    except EOFError:
        logging.warning('Input buffer is empty!')
    except StopIteration:
        pass

    output_line: str = get_output_line(data_path.get_output_buffer(), True)

    get_output_line(data_path.get_output_buffer(), True)

    logging.info('output_buffer: %s', output_line)
    return output_line, instr_counter, control_unit.tick_counter


def main(args):
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args

    bin_lines: list[str] = read_bin_code_from_file(code_file, 4)

    bin_lines = list(map(lambda line: ascii_code_to_binline(line), bin_lines))

    init_data, instructions = deserialize_bin_lines_list(bin_lines)

    input_tokens: list[str] = read_char_list_from_file(input_file)
    input_tokens: list[int] = list(map(lambda c: ord(c), input_tokens))

    output, instr_counter, ticks \
        = simulation(init_data, instructions, input_tokens, 1024, limit=100000)

    print(output)
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
