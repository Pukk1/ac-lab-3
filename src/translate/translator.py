#!/usr/bin_parsing/python3
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=invalid-name                # сохраним традиционные наименования сигналов
# pylint: disable=consider-using-f-string     # избыточный синтаксис

"""Транслятор asm в машинный код"""

import re
import sys
from typing import Optional

from src.bin_parsing.bin_ser import create_init_bin_data, create_bin_instructions, binline_to_ascii_code
from src.isa import Opcode, Instruction, OpcodeOperandsType, OpcodeInfo
from src.translate.translation_regex import is_section_instr, get_section_name, is_label_instr, is_comment_instr, \
    is_comment_or_label, get_opcode_regex, OPCODE_OPERAND_TYPE_VIEW
from src.utils import number_to_bin, write_code_to_file, write_code_with_mnemonics


class LabelAddress:
    """вспомогательная структура для хранения меток в коде в структурном виде"""

    def __init__(self, section: str, instr_line: int):
        self.section: str = section
        self.instr_line: int = instr_line


def get_opcode(line: str) -> Optional[Opcode]:
    """получить код операции для строки"""
    for opcode in Opcode:
        opcode: Opcode
        if re.match(get_opcode_regex(opcode), line) is not None:
            return opcode
    return None


def get_args_sub_str(line: str, opcode: Opcode) -> str:
    """получить подстроку набора аргументов из строки с инструкцией"""
    args = re.split(get_opcode_regex(opcode), line)[1]
    args = args.strip()
    return args


def get_args_list(line: str, opcode: Opcode) -> list[str]:
    args_sub_str = get_args_sub_str(line, opcode)
    args = args_sub_str.split(',')
    args = list(map(lambda it: it.strip(), args))
    if args[0] == '':
        # у команды нет аргументов (чтобы не выводить: '')
        return []
    return args


def get_opcode_arg_type(args: list[str], opcode: Opcode, line_number: int) -> OpcodeOperandsType:
    """получить тип набора аргументов для представленных для инструкции"""
    args_sub_str = ', '.join(args)
    opcode_info: OpcodeInfo = opcode.value
    for operand_type in opcode_info.available_types:
        if re.match(OPCODE_OPERAND_TYPE_VIEW[operand_type], args_sub_str) is not None:
            return operand_type
    assert False, 'Operands type not found for args substring: ' + args_sub_str + ' line_number=' + str(line_number)


def create_code_lines_list(program_text: str) -> list[str]:
    program_text = program_text.strip()
    instructions = program_text.split('\n')
    instructions: list[str] = list(map(lambda it: it.strip(), instructions))
    return instructions


def create_labels_lists(lines: list[str]) -> dict[str, LabelAddress]:
    """создать общий список всех меток в программе"""
    available_sections: list[str] = ['data', 'text']

    labels: dict[str, LabelAddress] = {}
    current_section: str = ''
    bin_lines_counter: int = 0
    for line_number, line in enumerate(lines):
        line_number += 1
        if is_section_instr(line):
            name = get_section_name(line)
            assert name in available_sections, 'Section=\"' + name + '\" not found in available names. line_number=' + \
                                               str(line_number)
            current_section = name
            available_sections.remove(name)
            # тк гарвардская а-ра, то при начале новой секции начинается новая физическая память
            bin_lines_counter = 0
            continue

        assert current_section != '', "Section should be selected on the first line"

        if is_label_instr(line):
            assert line not in labels, 'Label ' + line + ' already exist'
            section_name = line[:-1]
            labels[section_name] = LabelAddress(current_section, bin_lines_counter)
            continue

        if is_comment_instr(line):
            continue

        bin_lines_counter += 1

    return labels


def change_label_to_address(args: list[str], labels: dict[str, LabelAddress], bin_lines_counter: int) -> list[str]:
    """заменить метки на адреса:
    + для меток из section .data - адреса абсолютные тк гарвардская архитектура не позволяет сделать относительные
    + для меток из section .text - относительные адреса (команды ветвления)
    """
    addressed_args: list[str] = []
    for arg in args:
        if not arg.isdigit() and arg in labels:
            if labels[arg].section == 'text':
                addressed_args.append(str(labels[arg].instr_line - bin_lines_counter))
            else:
                addressed_args.append(str(labels[arg].instr_line))
        else:
            addressed_args.append(arg)
    return addressed_args


def change_regs_name_to_number(args: list[str]) -> list[int]:
    """замена названий регистров их порядковым номером"""
    result_list: list[int] = []
    for arg in args:
        reg_num: int
        if re.match(r'^reg[0-4]$', arg):
            reg_num = int(re.split(r'reg', arg)[1])
        else:
            reg_num = int(arg)
        result_list.append(reg_num)
    return result_list


def create_instructions(code_lines: list[str], labels: dict[str, LabelAddress]) -> list[Instruction]:
    """создание списка структур Instruction на основе исходного кода,
     для более удобного структурного представления программы
     """
    current_section: str = ''
    bin_lines_counter: int = 0
    instructions: list[Instruction] = []
    for line_number, line in enumerate(code_lines):
        line_number += 1
        if is_section_instr(line):
            current_section = get_section_name(line)
            continue

        if current_section == 'text':
            if is_comment_or_label(line):
                continue

            opcode: Optional[Opcode] = get_opcode(line)
            assert opcode is not None, "Unknown command: " + line + ' line_number=' + str(line_number)
            opcode: Opcode
            args: list[str] = get_args_list(line, opcode)
            args: list[str] = change_label_to_address(args, labels, bin_lines_counter)
            args_type = get_opcode_arg_type(args, opcode, line_number)

            # if args_type is OpcodeOperandsType.REG_CONST_REG:
            #     args_type = OpcodeOperandsType.REG_REG_CONST
            #     args[1], args[2] = args[2], args[1]

            args: list[int] = change_regs_name_to_number(args)

            instructions.append(Instruction(opcode, args_type, args))

            bin_lines_counter += 1

    return instructions


def translate(program_text: str) -> tuple[list[str], list[str]]:
    """трансляция программы в список машинных слов, соответствующих командам
    + для более удобного чтения список мнемоник бинарных команд"""
    lines: list[str] = create_code_lines_list(program_text)
    labels: dict[str, LabelAddress] = create_labels_lists(lines)

    bin_data, data_mnemonics = create_init_bin_data(lines)
    # указатель на то, сколько строк инициализируют память данных
    code: list[str] = [number_to_bin(len(bin_data), 32)]
    mnemonics: list[str] = [str(len(bin_data)) + ' - init num']
    code.extend(bin_data)
    mnemonics.extend(data_mnemonics)
    instructions: list[Instruction] = create_instructions(lines, labels)
    bin_instructions, mnemonics_instructions = create_bin_instructions(instructions)
    mnemonics_instructions = list(map(lambda instr: str(instr), instructions))
    code.extend(bin_instructions)
    mnemonics.extend(mnemonics_instructions)
    code = list(map(lambda it: binline_to_ascii_code(it), code))
    return code, mnemonics


def main(args: list):
    assert len(args) == 2, "Wrong arguments: translator.py <input_file> <target_file>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as f:
        source = f.read()

    code, mnemonics = translate(source)
    print("source LoC:", len(source.split()), "code instr:", len(code))
    write_code_to_file(target, code)
    write_code_with_mnemonics(target, code, mnemonics)


if __name__ == '__main__':
    main(sys.argv[1:])
