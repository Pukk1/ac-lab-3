section .data
section .text
start:
	read reg1
	print reg1
	jmp start
end:
	hlt
