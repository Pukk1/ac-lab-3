from constants.error_msg import ILLEGAL_BIN_NUMBER


def number_to_bin(value: int, word_length: int) -> str:
    # операции по получению бинарного представления числа =====
    if value < 0:
        value = abs(value) - 1
        number = bin(abs(value)).replace('0b', '')
        number = (word_length - len(number)) * '0' + number
        new_number: str = ''
        for c in number:
            if c == '0':
                new_number += '1'
            else:
                new_number += '0'
            number = new_number
    else:
        number = bin(abs(value)).replace('0b', '')
        number = (word_length - len(number)) * '0' + number
    # =========================================================
    return number


def bin_to_number(value: str, extra_code: bool) -> int:
    if not extra_code or value[0] == '0':
        return int('0b' + value, 2)
    abs_value_bin: str = ''
    for i in value:
        if i == '0':
            abs_value_bin += '1'
        else:
            abs_value_bin += '0'
    abs_value: int = int('0b' + abs_value_bin, 2)
    return (abs_value + 1) * -1


def write_list_to_file(filename: str, lines: list[str], join_str: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(join_str.join(lines))


def write_code_to_file(filename: str, bin_code: list[str]) -> None:
    # with open(filename, "w", encoding="utf-8") as file:
    #     file.write(''.join(bin_code))
    write_list_to_file(filename, bin_code, '')


def write_code_with_mnemonics(filename: str, bin_code: list[str], mnemonics: list[str]) -> None:
    res_lines: list[str] = []
    for i, line in enumerate(bin_code):
        res_lines.append(line)
        res_lines[i] += ' #' + mnemonics[i]
    dot_index: int = filename.rfind('.')
    filename = filename[:dot_index] + '_with_mnemonics.mnemonics'
    write_list_to_file(filename, res_lines, '\n')


def read_bin_code_from_file(filename: str, word_size: int) -> list[str]:
    lines: list[str] = []
    with open(filename, encoding="utf-8") as file:
        file_text: str = file.read()
        file_text = file_text.strip()
        # lines = file_text.split('\n')
        if len(file_text) % word_size != 0:
            assert False, ILLEGAL_BIN_NUMBER.format(len(file_text))
        for i in range(0, int(len(file_text) / word_size)):
            lines.append(file_text[:word_size])
            file_text = file_text[word_size:]
    return lines


def read_char_list_from_file(filename: str) -> list[str]:
    char_list: list[str] = []
    with open(filename, encoding="utf-8") as file:
        for c in file.read():
            char_list.append(c)
        return char_list
