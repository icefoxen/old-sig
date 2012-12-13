\ The second test for Sig.
\ Does memory-stuff.  Fun!
\
\ Simon Heath
\ 30/5/2003

%%var bop 10

: foo
  10 20 30 + + emit ;

: main
   10 4 * alloc    \ Allocate 10 cells, seeing as we don't have a 'cells' word
   dup 0x40 swap ! \ Stick the value '40' in it.
   @ emit          \ And get it back
   foo
   40 50 < 40 + emit
   40 0xFFFFFFFF u< 40 + emit
   ;
