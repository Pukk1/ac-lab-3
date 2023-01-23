section .data
a:
    word 1
section .text
    ld reg1, a
    add reg1, reg1, 10
    st reg1, a
    hlt