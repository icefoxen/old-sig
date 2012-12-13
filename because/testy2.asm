global main
global foo
extern ulessequal
extern ugreaterequal
extern uless
extern ugreater
extern getdouble
extern putdouble
extern getchar
extern putchar
extern free
extern alloc
extern get
extern put
extern depth
extern orsig
extern andsig
extern drop
extern tuck
extern nip
extern rot
extern swap
extern over
extern dup
extern emit
extern twomulsig
extern twodivsig
extern equalzerosig
extern lessequalsig
extern greaterequalsig
extern lesssig
extern greatersig
extern notequalsig
extern equalsig
extern divsig
extern mulsig
extern subsig
extern addsig
extern _pushstack, _popstack, _initstack

foo:
mov eax, 10
call _pushstack
mov eax, 20
call _pushstack
mov eax, 30
call _pushstack
call addsig
call addsig
call emit
ret


main:
call _initstack
mov eax, 10
call _pushstack
mov eax, 4
call _pushstack
call mulsig
call alloc
call dup
mov eax, 0x40
call _pushstack
call swap
call put
call get
call emit
call foo
mov eax, 40
call _pushstack
mov eax, 50
call _pushstack
call lesssig
mov eax, 40
call _pushstack
call addsig
call emit
mov eax, 40
call _pushstack
mov eax, 0xFFFFFFFF
call _pushstack
call uless
mov eax, 40
call _pushstack
call addsig
call emit
ret

