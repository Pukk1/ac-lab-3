# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=import-error  # не видит мои модули
# pylint: disable=line-too-long
"""Интеграционные тесты транслятора и машины
"""
import unittest

import pytest

import machine
import translate.translator
from isa import Opcode, OpcodeOperandsType


@pytest.mark.golden_test("golden/unit/translate/*.yml")
def test_translation(golden):
    code, _ = translate.translator.translate(golden["source"])
    assert code == golden.out["code"]


class TranslationTest(unittest.TestCase):

    def test_get_opcode(self):
        opcode = translate.translator.get_opcode('add  reg1  , reg1,   reg1')
        self.assertEqual(opcode, Opcode.ADD)
        opcode = translate.translator.get_opcode('sub  reg1  , reg1,   reg1')
        self.assertEqual(opcode, Opcode.SUB)
        opcode = translate.translator.get_opcode('mul  reg1  , reg1,   reg1')
        self.assertEqual(opcode, Opcode.MUL)
        opcode = translate.translator.get_opcode('jmp asd')
        self.assertEqual(opcode, Opcode.JMP)
        opcode: Opcode = translate.translator.get_opcode('asdasd  reg1  , reg1,   reg1')
        self.assertEqual(opcode, None)

    def test_get_args_sub_string(self):
        sub_str = translate.translator.get_args_sub_str('add  reg1  , reg1,   reg1', Opcode.ADD)
        self.assertEqual(sub_str, 'reg1  , reg1,   reg1')

    def test_get_args_list(self):
        args = translate.translator.get_args_list('add  reg1  , reg1,   reg1', Opcode.ADD)
        self.assertEqual(args, ['reg1', 'reg1', 'reg1'])

    def test_get_opcode_arg_type(self):
        op_type = translate.translator.get_opcode_arg_type(['reg1', 'reg2', 'reg3'], Opcode.ADD, 0)
        self.assertEqual(op_type, OpcodeOperandsType.REG_REG_REG)
        op_type = translate.translator.get_opcode_arg_type(['reg1', 'reg2', '10'], Opcode.ADD, 0)
        self.assertEqual(op_type, OpcodeOperandsType.REG_REG_CONST)
        op_type = translate.translator.get_opcode_arg_type(['reg1', '10'], Opcode.LD, 0)
        self.assertEqual(op_type, OpcodeOperandsType.REG_CONST)
        op_type = translate.translator.get_opcode_arg_type(['reg1'], Opcode.PRINT, 0)
        self.assertEqual(op_type, OpcodeOperandsType.REG)
        op_type = translate.translator.get_opcode_arg_type(['10'], Opcode.JMP, 0)
        self.assertEqual(op_type, OpcodeOperandsType.CONST)
        op_type = translate.translator.get_opcode_arg_type([], Opcode.HLT, 0)
        self.assertEqual(op_type, OpcodeOperandsType.NONE)


class TestMachine(unittest.TestCase):
    def test_alu_zero_flag(self):
        alu = machine.Alu()
        alu.op1 = 10
        alu.op2 = 11
        alu.execute(Opcode.MOD)
        self.assertEqual(alu.res, 10)
        self.assertEqual(alu.zero, False)
        alu.execute(Opcode.DIV)
        self.assertEqual(alu.res, 0)
        self.assertEqual(alu.zero, True)

    def test_reg_file(self):
        reg_file = machine.RegFile()
        reg_file.set_reg_value(0, 10)
        reg_file.choice_ops(0, 0)
        self.assertEqual(reg_file.op1, 0)
        self.assertEqual(reg_file.op2, 0)

        reg_file.set_reg_value(1, 15)
        reg_file.set_reg_value(2, 30)
        reg_file.choice_ops(1, 2)
        self.assertEqual(reg_file.op1, 15)
        self.assertEqual(reg_file.op2, 30)

    def test_data_mem_read(self):
        init_data = [0] * 10
        init_data[1] = 111
        data_path = machine.DataPath(10, init_data, [])
        data_path.alu.res = 1
        data_path.mem_read()
        self.assertEqual(data_path.data_mem.res, 111)

    def test_data_mem_write(self):
        init_data = [0] * 10
        data_path = machine.DataPath(10, init_data, [])
        data_path.reg_file.op2 = 111
        data_path.alu.res = 1
        data_path.mem_write()
        self.assertEqual(data_path.data_mem.mem[1], 111)
