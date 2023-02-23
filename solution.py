# Проект Эйлера
# Задача 5
# 2520 - самое маленькое число, которое делится без остатка на все
# числа от 1 до 10.
# Какое самое маленькое число делится нацело на все числа от 1 до 20?
# Ответ: 232792560

maxRange = 20
count = 1
sum = 20
lstCount = 19

tmpReg1 = sum
tmpReg2 = lstCount
tmpReg3 = count

while tmpReg2 != 1:
    tmpReg4 = tmpReg1
    while tmpReg1 % tmpReg2 != 0:
        tmpReg1 += tmpReg4
    tmpReg3 += 1
    tmpReg2 = tmpReg3-20
    tmpReg2 *= -1

print(tmpReg1)

# Решение.
# 1. Берем самое большое число из списка (20) и делим его на следующее
# число из списка (19),
# 2. если делиться с остатком, то самое большое число
# прибавляем к самому себе (20+20=40),
# 3. получившуюся сумму (40) делим на следующее число (19) так до тех пор пока
# не разделиться без остатка.
# 4. Получившуюся сумму пробуем разделить на следующее число (18).
# 5. если делиться с остатком, то сумму прибавляем к самой себе,
# 6. получившуюся сумму делим на число (18) так до тех пор пока
# не разделиться без остатка...
# 7. Переходим к пункту 4 заменив число на следующее (17)