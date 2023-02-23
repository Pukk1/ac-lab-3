# Assembler. Транслятор и модель

- ФИО.
- `asm | risc | harv | hw | instr | binary | stream | mem | prob5`

## Язык программирования

``` ebnf
<program> ::= <section_data> <section_text> | <section_text> <section_data> | <section_text>

<section_data> ::= "section .data\n" <declaration_line>*

<section_text> ::= "section .text\n" <instruction_line>*

<declaration_line> ::= <comment>* "\t"* (<data_label> | <declaration>) "\n" <comment>*

<instruction_line> ::= <comment>* "\t"* (<text_label> | <instruction>) "\n" <comment>*

<comment> ::= "\t"* "#" <char>* "\n"

<data_label> ::= <data_label_name> ":"

<declaration> ::= "word" <number>

<text_label> ::= <text_label_name> ":"

<data_label_name> ::= [a-zA-Z]+

<text_label_name> ::= [a-zA-Z]+
            
<instruction> ::=  <3_operand_instruction> | <2_operand_instruction> | <1_operand_instruction> | <0_operand_instruction>       
            
<3_operand_instruction> ::= ("add" | "sub" | "mul" | "div" | "mod") " " (<reg_reg_const_op_set> | <reg_reg_reg_op_set>)

<reg_reg_const_op_set> ::= <register> ", " <register> ", "  (data_label_name | number)

<reg_reg_reg_op_set> ::= <register> ", " <register> ", " <register>

<2_operand_instruction> ::= ("ld" | "st") " " <register> ", " (data_label_name | number)

<1_operand_instruction> ::= <1_operand_const_instruction> | <1_operand_reg_instruction>

<1_operand_const_instruction> ::= ("jmp" | "beq" | "bne") " " <text_label_name>

<1_operand_reg_instruction> ::= ("print" | "read") " " <register>

<register> ::= "reg0" | "reg1" | "reg2" | "reg3" | "reg4" 
          
<number> ::= [-2^31; 2^31 - 1]

<char> ::= "<any UTF-8 symbol>"


```

Декларации из **section data** выполняются последовательно. Операции:

- `word <num>` -- записать num в ячейку памяти номер `%номер word%`;

Поддерживаемые аргументы:

- для аргументов **num** число в диапазоне [-2^31; 2^31 - 1]

Код из **section text** выполняется последовательно. Операции:

- `add <reg1> <reg2> <reg_const>` -- прибавить `reg_const` к регистру `reg2` и записать в регистр `reg1`
- `sub <reg1> <reg2> <reg_const>` -- вычесть `reg_const` из регистра `reg2` и записать в регистр `reg1`
- `div <reg1> <reg2> <reg_const>` -- записать целую часть от деления регистра `reg2` на `reg_const` в регистр `reg1`
- `mod <reg1> <reg2> <reg_const>` -- записать остаток от деления регистра `reg2` на `reg_const` в регистр `reg1`
- `mul <reg1> <reg2> <reg_const>` -- записать произведение `reg_const` и `reg2` в регистр `reg1`
- `jmp <text_label>` -- безусловный переход на метку `text_label`
- `beq <text_label>` -- переход на метку `text_label`, если флаг Z == True
- `bne <text_label>` -- переход на метку `text_label`, если флаг Z != True
- `print <reg1>` -- распечатать в поток вывода значение из `reg1`
- `read <reg1>` -- прочитать в `reg1` значение из потока ввода
- `ld <reg1> <const_data_label>` -- прочитать в `reg1` значение из памяти данных по адресу `const_data_label`
- `st <reg1> <const_data_label>` -- записать `reg1` в память данных по адресу `const_data_label`
- `hlt` -- завершить выполнение программы

Поддерживаемые аргументы:

- для аргументов **reg[1-2]** регистры `r0`, `r1`, `r2`, `r3`, `r4`
- для аргументов **reg_const** регистр из reg[1-2] или целое число [-2^15, 2^15]
- для аргументов **text_label** имя метки, определённой в блоке кода
- для аргументов **const_data_label** целое число [-2^15, 2^15] или имя метки, определённой в блоке данных

Дополнительные конструкции:

- `# <any sequence>` - комментарий
- `section text` - объявление секции кода
- `section data` - объявление секции данных
- `<label>:` - метки для переходов / названия переменных

Примечания:

- Исполнение кода начинается с первой инструкции в section text
- При введение других инструкций поведение не специфицируется и вызывает ошибку трансляции.

## Организация памяти

Модель памяти процессора:

1. Память команд. Машинное слово -- 32 бита (в бинарном формате). На уровне процессора бинарный формат преобразуется в
   словарь для более удобного взаимодействия.
2. Память данных. Машинное слово -- 32 бита, знаковое. Линейное адресное пространство. Реализуется списком чисел.

Типы адресации:

1. Абсолютная - используется для адресации в памяти данных
2. Относительная - используется для адресации в памяти инструкций (позволяет сделать программу перемещаемой)

## Система команд

Особенности процессора:

- Машинное слово -- 32 бит, знаковое;
- Регистры:
    - управляются с помощью устройства RegFile (регистровый файл)
    - RegFile может принимать сигналы op1, op2, res
    - сигнал op1 - значение какого регистра будет передано на шину op1
    - сигнал op2 - значение какого регистра будет передано на шину op2
    - сигнал res - в какой регистр запишется значение с шины res_data
    - обработка сигналов op1 и op2 и передача занчений на шину происходит в рамках одного такта
    - обработка сигнала res и сохранение значение с шины res_data требует защёлкивания регистра
    - всего 5 регистров: reg0, reg1, reg2, reg3, reg4
    - reg0 - hardware_zero (всегда содержит значение 0)
    - в любой из регистров можно писать и из любого читать
- Память данных:
    - адресуется через разультат выполнения выражения на алу;
    - может быть записана:
        - из региста, обозначенного как op2 в регистровом файле;
    - может быть прочитана в регистр, обозначенный как res в регистровом файле;
- АЛУ:
    - на левый вход алу вместо регистра op2 из регистрового файла может быть подана константа;
    - на правый вход алу подаётся регистр op1 из регистрового файла;
    - АЛУ поддерживает операции: ADD, SUB, MUL, DIV, MOD
    - любая операция на АЛУ выставляет флаг Z в True или False
- Ввод-вывод -- ввод/вывод через память (адрес ячейки ввода = размер памяти данных - 2, адрес ячейки вывода = 
размер памяти данных - 1), токенизирован, символьный (при возможности приведения числа к соответствующему ascii
  коду).
- `program_counter` -- счётчик команд:
    - инкрементируется после каждой инструкции или перезаписывается инструкцией перехода.

### Набор инструкций

Более подробное описание команд в пункте **Язык программирования**
Набор инструкций соответствует основным принципам RISC-архитектуры

- `add <reg1> <reg2> <reg_const>` -- 1 такт
- `sub <reg1> <reg2> <reg_const>` -- 1 такт
- `div <reg1> <reg2> <reg_const>` -- 1 такт
- `mod <reg1> <reg2> <reg_const>` -- 1 такт
- `mul <reg1> <reg2> <reg_const>` -- 1 такт
- `jmp <text_label>` -- 1 такт
- `beq <text_label>` -- 1 такт
- `bne <text_label>` -- 1 такт
- `print <reg1>` -- 1 такт
- `read <reg1>` -- 1 такт
- `ld <reg1> <const_data_label>` -- 2 такт
- `st <reg1> <const_data_label>` -- 1 такт
- `hlt` -- 1 такт

### Кодирование инструкций

- Машинный код сериализуется в бинарный код.
- 32 бита - одна инструкция со всеми её операндами.
- Первые 32 бита в бинарном коде - количество слов идущих после этого, которые используются для инициализации памяти
  данных.
- После инструкций по инициализации идут машинные коды команды.
- Структура машинного слова определяется Opcode-ом команды и типом набора её операнд.
- Правила формирования структуры машинного слова для серилизации инструкций:
    - 0-3 бит под код opcode
    - 4-й бит под специфику команды (вид адрессации например)
    - 5-7 бит под тип набора операндов
- В зависимости от типа набора операндов:
    - NONE - 8-31 бит пустые
    - CONST - 8-11 бит пустые (либо под расширение специфики команды), 12-15 пустые, 16-31 бит заняты константой
    - REG_CONST - 8-11 бит пустые (либо под расширение специфики команды), 12-27 бит константа, 28-31 бит регистр
    - REG_REG_REG - 8-19 пустые, 20-23 бит под регистр, 24-27 бит под регистр, 28-31 бит под регистр
    - REG_REG_CONST - 8-23 бит под константу, 24-27 бит под регистр, 28-31 бит под регистр
    - REG_REG - 8-23 бит пустые, 24-27 бит под регистр, 28-31 бит под регистр
    - REG - 8-27 бит пустые, 28-31 бит под регистр

Пример:

00000001000000111110100010000010

Где:

opcode=SUB operands_type=REG_REG_CONST operands=['0', '1', '1000']

Типы данные в модуле [isa](src/isa.py), где:

- `Opcode` -- перечисление кодов операций и возможных для них наборов аргументов;
- `OpcodeOperandsType` -- перечисление возможных наборов аргументов для операций;
- `Instruction` -- структура для хранения информации о типе операции, её наборе аргументов и их типе

## Транслятор

Реализовано в модуле: [translation](./translation.py)

Этапы трансляции (функция `translate`):

1. создание списка всех меток в коде (секции даты и кода)
2. создание бинарного представления data секции
3. создание списка инструкций (структура для хранения типа операции, типа набора её операндов, занчений операндов в
   наборе). Валидация кода программы, во время создания инструкций.
4. создание бинарного представления набора инструкций
5. объединение бинарных представлений обоих секций и запись результата в файл

Правила генерации машинного кода:

- одна инструкция процессора -- одна инструкция в коде;
- инструкция и все её операнды хранятся в одном машинном слове
- команды из **section data** используются для заполнения памяти данных;
- запись в память данных происходит начиная с первой команды из **section data**
- запись в память команд происходит начиная с первой команды из **section text**;

## Модель процессора

Реализовано в модуле: [machine](src/machine.py).
Процессор разработан с целью соответсвовать RISC-архитектуре исполняемых на нём команд.
Бинарные команды, с целью упращения, при входе в процессор десерелизуются обратно в набор инструкций.

### Схема DataPath и ControlUnit

![https://drive.google.com/file/d/1UAJ1Mogn2baRUmme73Vbf2_NGS0mOF4n/view?usp=sharing](/image.png "Схема DataPath и ControlUnit")

### DataPath

Реализован в классе `DataPath`.

- `data_mem` -- однопортовая, поэтому либо читаем, либо пишем.
  - `data_mem.res` -- результат чтения из памяти сохраняется сюда и подаётся на шину res_data
- `input` -- вызовет остановку процесса моделирования, если буфер входных значений закончился.
- `reg_file` -- регистровый файл, устройство с помощью сигналов op1, op2, res манипулирующее регистрами reg0-reg4
  - `reg_file.op1` - регистр, данные из которого идут на правый вход алу
  - `reg_file.op2` - регистр, данные из которого идут на левый вход алу
- `alu` -- выполняет арифметические операции
  - `alu.left` -- левые вход АЛУ
  - `alu.right` -- правый вход АЛУ
  - `alu.res` -- результат выполнения арифметической операции на АЛУ
  - `alu.zero` -- нулевой флаг выполняемый после каждой операции
- `pc` - счётчик инструкций
- `instr_mem` - память инструкций
- `control_unit` - модуль управления работой процессора
  - `control_unit.const` - константа, которая может быть принята как один из операндов в АЛУ с использованием сигнала sig_const

Сигналы:
- `sig_next` - если пришёл, то PC - итерируется, нет - заменяет значение на новое (ветвление)
- `sig_const` - если пришёл, то на левый вход алу идёт константа из control unit, нет - значение из reg_file.op2
- `sig_write` - сигнал на запись в память, если не пришёл, то происходит чтение
- `sig_read_data` - сигнал на получение данных из памяти, если не пришёл, то на шину res_data поступает значение alu.res

Сигналы RegFile:
- `op1` - указатель значение какого регистра следует передать на reg_file.op1
- `op2` - указатель значение какого регистра следует передать на reg_file.op2
- `res` - указатель в какой регистр нужно записать данные с шины res_data

Флаги:

- `zero` -- отражает наличие нулевого значения в аккумуляторе.

### ControlUnit

Реализован в классе `ControlUnit`.

- Hardwired (реализовано полностью на python).
- Моделирование на уровне инструкций.
- Трансляция инструкции в последовательность сигналов: `decode_and_execute_instruction`.
- `step_counter` необходим для многотактовых команд:
    - в классе `ControlUnit` отсутствует, т.к. моделирование производится на уровне инструкций.

Сигнал:

- `latch_program_counter` -- сигнал для обновления счётчика команд в ControlUnit.

Особенности работы модели:

- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования ограничено hardcoded константой.
- Остановка моделирования осуществляется при помощи исключений:
    - `EOFError` -- если нет данных для чтения (ввода);
    - `StopIteration` -- если выполнена инструкция `hlt`.
- Управление симуляцией реализовано в функции `simulate`.

## Апробация

В качестве интеграционных тестов реализовано 4 алгоритма:

1. [hello world](files/helloworld.asm).
2. [cat](files/cat.asm) -- программа `cat`, повторяем ввод на выводе.
3. [prob1](files/alg.asm) -- рассчитать сумму делителей 3 или 5, меньших 1000
4. [test_st](files/test_st.asm) -- проверяет корректность работы команды st (единственная не покрытая предыдущими тестами сложная (не арифметическая) операция)

Юнит-тесты реализованы тут:
[unit_test](unit_test.py)

CI:

``` yaml
lab3-example:
  stage: test
  image:
    name: python-tools
    entrypoint: [""]
  script:
    - pip install pytest-golden
    - python3-coverage run -m pytest --verbose
    - find . -type f -name "*.py" | xargs -t python3-coverage report
    - find . -type f -name "*.py" | xargs -t pep8 --ignore=E501
    - find . -type f -name "*.py" | xargs -t pylint --disable C0301,C0115,C0116,R0903,W0108,R1720,C0103,C0114,C0209
```

где:

- `python3-coverage` -- формирование отчёта об уровне покрытия исходного кода.
- `pytest` -- утилита для запуска тестов.
- `pep8` -- утилита для проверки форматирования кода. `E501` (длина строк) отключено, но не следует этим злоупотреблять.
- `pylint` -- утилита для проверки качества кода. Некоторые правила отключены в отдельных модулях с целью упрощения
  кода.
- Docker image `python-tools` включает в себя все перечисленные утилиты. Его конфигурация: [Dockerfile](./Dockerfile).

Пример использования и журнал работы процессора на примере `cat`:

``` console
> cd ac-lab-3
> cat files/input
asd
> cat files/cat.asm 
section .data
section .text
start:
	read reg1
	print reg1
	jmp start
end:
	hlt
> ./translate/translator.py files/cat.asm files/bin.bin
source LoC: 13 code instr: 5
> cat bin.bin
0000000000000000000000000000000000010000000000000000000011001100000100000000000000000000110010111111111111111110000000000010011000000000000000000000000000000000
> ./machine.py files/bin.bin files/input
DEBUG:root:READ REG [1] {TICK: 0, PC: 0, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 0, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:PRINT REG [1] {TICK: 1, PC: 1, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 97, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:JMP CONST [-2] {TICK: 2, PC: 2, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 97, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:READ REG [1] {TICK: 3, PC: 0, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 97, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:PRINT REG [1] {TICK: 4, PC: 1, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 115, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:JMP CONST [-2] {TICK: 5, PC: 2, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 115, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:READ REG [1] {TICK: 6, PC: 0, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 115, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:PRINT REG [1] {TICK: 7, PC: 1, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 100, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:JMP CONST [-2] {TICK: 8, PC: 2, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 100, REG2: 0, REG3: 0, REG4: 0}
DEBUG:root:READ REG [1] {TICK: 9, PC: 0, ALU_RES: 0, DATA_MEM[ALU_RES]: 0, REG1: 100, REG2: 0, REG3: 0, REG4: 0}
WARNING:root:Input buffer is empty!
INFO:root:output_buffer: asd
asd
instr_counter:  9 ticks: 9
```

| ФИО | алг.       | LoC | code байт | code инстр. | инстр. | такт. | вариант |
|-----|------------|-----|-----------|-------------|--------|-------|---------|
| ФИО | helloworld | 82  | 992       | 31          | 21     | 31    | ...     |
| ФИО | cat        | 13  | 160       | 5           | 9      | 9     | ...     |
| ФИО | prob1      | 57  | 576       | 18          | 9110   | 9112  | ...     |
