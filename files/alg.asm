section .data
it:
    word 3
sum:
    word 0
section .text
start:
    ld reg1, it
    ld reg2, sum
startif:
    mod reg0, reg1, 15
    beq addsum
    mod reg0, reg1, 3
    beq addsum
    mod reg0, reg1, 5
    beq addsum
iteration:
    add reg1, reg1, 1
    sub reg0, reg1, 1000
    bne startif
    print reg2
    hlt
addsum:
    add reg2, reg2, reg1
    jmp iteration

