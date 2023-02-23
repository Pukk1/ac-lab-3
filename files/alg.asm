section .data
maxrange:
    word 20
count:
    word 1
sum:
    word 20
lstcount:
    word 19
section .text
start:
    ld reg1, sum
    ld reg2, lstcount
    ld reg3, count
startloop:
    sub reg0, reg2, 1
    bne loopbody
    print reg1
    hlt
loopbody:
    add reg4, reg1, reg0
adderloop:
    mod reg0, reg1, reg2
    beq loopcont
    add reg1, reg1, reg4
    jmp adderloop
loopcont:
    add reg3, reg3, 1
    sub reg2, reg3, 20
    mul reg2, reg2, -1
    jmp startloop
