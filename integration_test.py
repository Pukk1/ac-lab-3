# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=line-too-long               # строки с ожидаемым выводом

"""Интеграционные тесты транслятора и машины
"""

import contextlib
import io
import logging
import os
import tempfile

import pytest

from src import machine
from src.translate import translator


# Тут используется подход golden tests. У него не самая удачная реализация для
# python: https://pypi.org/project/pytest-golden/ , но знать об этом подходе
# крайне полезно.
#
# Принцип работы следующий: во внешних файлах специфицируются входные и выходные
# данные для теста. При запуске тестов происходит сравнение и если выход
# изменился -- выводится ошибка.
#
# Если вы меняете логику работы приложения -- то запускаете тесты с ключём:
# `cd src/brainfuck && true && pytest . -v --update-goldens`
#
# Это обновит файлы конфигурации и вы можете закомитить изменения в репозиторий,
# если они корректные.
#
# Формат файла описания теста -- YAML. Поля определяются самим тестом:
#
# - source -- исходный код на вход
# - input -- данные на ввод процессора
# - code -- машинный код на выходе из ранслятора
# - output -- стандартный вывод программ
# - log -- журнал программы
@pytest.mark.golden_test("golden/integration/*.yml")
def test_whole_by_golden(golden, caplog):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.bf")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.o")
        target_mnem = os.path.join(tmpdirname, "target_with_mnemonics.mnemonics")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        # Запускаем транлятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main([source, target])
            print("============================================================")
            machine.main([target, input_stream])

        # Выходные данные также считываем в переменные.
        with open(target, encoding="utf-8") as file:
            code = file.read()

        with open(target_mnem, encoding="utf-8") as file:
            mnem_code = file.read()

        # Проверяем что ожидания соответствуют реальности.
        assert code == golden.out["code"]
        assert mnem_code == golden.out["code_with_mnem"]
        assert stdout.getvalue() == golden.out["output"]
        assert caplog.text == golden.out["log"]
