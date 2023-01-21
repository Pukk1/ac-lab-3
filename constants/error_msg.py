"""Набор текстовых представлений ошибок для assert'ов"""
UNKNOWN_OPERATION: str = "Unknown operation '{}' in line {}!"
WRONG_ARGS_NUM: str = "Wrong number of operands near '{}', line {}. {} expected, {} got."
MULTIPLE_SEMICOLON: str = "Multiple ';' in line {}"
INVALID_SYNTAX: str = "Invalid syntax, line {}."
DUPLICATE_LABEL: str = "Duplicate label '{}'!"
INVALID_OPERAND: str = "Invalid operand '{}', line {}"
UNKNOWN_SECTION: str = "Unknown section '{}', line {}"
TOO_BIG_INPUT: str = "Input token is out of bound: {}"
SEG_FAULT: str = "Trying to reach reserved memory: {}"
INTERNAL_ERR: str = "Internal error while latching {}"
NEGATIVE_SIZE_ERR: str = "Data_memory size should be non-zero"
TOO_LONG_EXEC: str = "Too long execution, increase limit!"
MISSING_START_LABEL: str = "Missing 'start' label!"