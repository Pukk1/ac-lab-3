section .data
tmp:
	word 0

section .text
start:
	read tmp
	print tmp
	jmp start
end:
	exit
