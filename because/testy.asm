global main
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
extern getsig
extern setsig
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

main:
call _initstack
mov eax, 32
call _pushstack
call emit
mov eax, 32
call _pushstack
call twomulsig
call emit
mov eax, 32
call _pushstack
call twodivsig
call emit
mov eax, 'a'
call _pushstack
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
call orsig
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
call andsig
call emit
mov eax, 10
call _pushstack
call emit
mov eax, 'a'
call _pushstack
call dup
call emit
call emit
mov eax, 10
call _pushstack
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
call swap
call emit
call emit
mov eax, 10
call _pushstack
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
mov eax, 'c'
call _pushstack
call rot
call emit
call emit
call emit
mov eax, 10
call _pushstack
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
mov eax, 'c'
call _pushstack
call tuck
call emit
call emit
call emit
mov eax, 10
call _pushstack
call emit
mov eax, 'a'
call _pushstack
mov eax, 'b'
call _pushstack
call over
call emit
call emit
call emit
mov eax, 10
call _pushstack
call emit
ret

