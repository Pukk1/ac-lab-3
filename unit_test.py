# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=import-error  # не видит мои модули
# pylint: disable=line-too-long
"""Интеграционные тесты транслятора и машины
"""

import pytest

import translate.translator


@pytest.mark.golden_test("golden/unit/translate/*.yml")
def test_translation(golden, caplog):
    code, mnemonics = translate.translator.translate(golden["source"])
    assert code == golden.out["code"]
