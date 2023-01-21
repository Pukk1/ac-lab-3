section .data
h:
	word 104
e:
	word 101
l:
	word 108
o:
	word 111
space:
	word 32
w:
	word 119
r:
	word 114
d:
	word 100
section .text
start:
    ld reg1, h
	print reg1
	ld reg1, e
	print reg1
	ld reg1, l
	print reg1
	print reg1
	ld reg1, o
	print reg1
	ld reg1, space
	print reg1
	ld reg1, w
	print reg1
	ld reg1, o
	print reg1
	ld reg1, r
	print reg1
	ld reg1, l
	print reg1
	ld reg1, d
	print reg1
	hlt

