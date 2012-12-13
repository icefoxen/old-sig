# because.py
# Sig compiler.  Sig is a Forth-like language (somewhat simplified) of my own
# design, and this compiles it to NASM assembly.
#
#
# Order to do things in:
#  Global variables and constants
#  Floating-point math
#  If/else/then, and case
#  begin/loop, do/while, and do/loop.  Plus continue and break.
#  Local variables
#  String and printing
# Semi-theoretical:
#  Namespaces
#  Error handling
#  GC --think 'bout it.
# 
# Simon Heath
# 29/5/2003


import string
import re


##############################################################################
###  VARIABLES  ##############################################################

# These don't work right yet; they're used for error messages
filename = "stdin"
lineno   = 0

# Function name lists 
# C'mon... for these builtins, there has GOTTA be a better way of defining
# them...
# Maybe this'll get fixed once I figure out the namespace junkin.
# Hmm... there are some important constants I need, also.  Things like
# 'space' and 'cr'...
bfuncs = [
   'addsig',
   'subsig',
   'mulsig',
   'divsig',
   'equalsig',
   'notequalsig',
   'greatersig',
   'lesssig',
   'greaterequalsig',
   'lessequalsig',
   'equalzerosig',
   'twodivsig',
   'twomulsig',
   'emit',
   'dup',
   'over',
   'swap',
   'rot',
   'nip',
   'tuck',
   'drop',
   'andsig',
   'orsig',
   'depth',
   'put',
   'get',
   'alloc',
   'free',
   'putchar',
   'getchar',
   'putdouble',
   'getdouble',
   'ugreater',
   'uless',
   'ugreaterequal',
   'ulessequal']
ufuncs = []
globalvars = []
localvars = []

# This is a list of all compiler declerations, such as variable declerations,
# gets put.
decls = []

# This is where all the file declerations, like extern/global and global vars,
# get put.
fileheader = ""

##############################################################################
###  UTILITY FUNCTIONS  ######################################################

# Signal an error.  Generally a syntax error of some kind
def error( st ):
   raise (filename + ", line " + str( lineno ) + ":\n" + st)

# Returns whether or not a string is a number
# Only handles integers, at the moment...
# Does hex numbers though!  ^_^  'Tis easy, 'cause NASM recognizes 'em, so no
# transformation is necessary
def isDigit( s ):
   if matchString( s, string.digits ):
      return 1
   # Check negative numbers too
   elif s[0] == '-' and matchString( s[1:], string.digits ):
      return 1
   elif isHex( s ):
      return 1
   else:
      return 0
      
# Returns whether or not a string is a hex number in the form of 0x####...
def isHex( x ):
   if x[:2] == '0x' and matchString( x[2:], string.hexdigits ):
      return 1
   # Check for negative numbers too   
   elif x[:3] == '-0x' and matchString( x[3:], string.hexdigits ):
      return 1
   else:
      return 0

# Returns true if all chars in str1 exist in str2
def matchString( str1, str2 ):
   for x in str1:
      if not str2.__contains__( x ):
         return 0
   return 1


# Recognizes characters preceeded by a '
# For instance, the strings "'f" and "'foo" would register as 'f'.
def isChar( c ):
   if c[0] == '\'' and string.printable.__contains__( c[1] ):
      return 1
   return 0


##############################################################################
###  BACKEND FUNCTIONS  ######################################################
# These all have to do with translating a list of tokens into assembly.


# Translates a word from Sig to assembly
# Very very simple once we set everything up.
def compword( word ):
   final = ""
   # If is a digit, we push it to the stack
   if isDigit( word ):
      final += "mov eax, " + str( word ) + "\ncall _pushstack\n"
   # Same with characters
   elif isChar( word ):
      final += "mov eax, '" + word[1] + "'\ncall _pushstack\n"
   # And global variables
   elif isGVar( word ): 
   # If it's a builtin function, we call it
   elif bfuncs.__contains__( word ):
      final += "call " + word + "\n"
   # Same with user functions
   elif ufuncs.__contains__( word ):
      final += "call " + word + "\n"
   else:
      error( "Unknown word: " + word )

   return final


# Translates a list of words from Sig to assembly.  Simple
def compwords( wordlist ):
   final = ""
   for x in wordlist:
      final += compword( x )
   return final


# Translates a function definition from Sig to assembly
# A function definition is a (name, [body]) tuple.
def compfuncdef( funcdef ):
   # First we grab the name and make it a label...
   final = "\n" + funcdef[0] + ":\n"
   # Check if the function is 'main'; if so, the stack needs to be inited
   if funcdef[0] == 'main':
      final += 'call _initstack\n'
   # Then we append the compiled body
   final += compwords( funcdef[1] )
   # And add a return instruction
   final += "ret\n"
   return final


# Compile a list of function definitions
def compfuncdefs( funclist ):
   final = ""
   for x in funclist:
      final += compfuncdef( x )
      final += "\n"
   return final


# Translates a : name ... ; list of tokens into a function definition and puts
# it in the user func list
# A function definition is a tuple: (name, [word1, word2, word3, ...])
def createfuncdef( words ):
   # Name is the second token
   name = words[1]
   # Body is all but the last token (to get rid of the terminating ';')
   body = words[:-1]
   # And also minus the first two tokens (the ': name' bit)
   body = body[2:]
   # Check to see no functions are overridden
   if ufuncs.__contains__( name ):
      error( "Redefining function " + name )
   elif bfuncs.__contains__( name ):
      error( "Redefining built-in function " + name
   # And make sure it doesn't match the ever-changing qualifications of
   # isDigit()
   elif isDigit( name ):
      error( "Function names cannot be numbers!" )
   # If it's good, append it to the user-function list.
   else:
      ufuncs.append( name )
   return (name, body)


# Translates a list of : name ... ; lists into a list of function definitions
def createfuncdefs( funclist ):
   final = []
   # Just loop createfuncdef() over a list
   for x in funclist:
      final.append( createfuncdef( x ) )
   return final


##############################################################################
###  FRONTEND FUNCTIONS  #####################################################
# These all have to do with translating arbitrary text into a valid list of
# tokens.


# Take an arbitrary list of words and pick out any function definitions in it.
# Returns a list of lists, with each inner list being an individual
# function definition
def findfuncdef( words ):
   final = []
   infunc = 0
   currentdef = []
   for x in words:
      # Check to see if we're already reading a function
      if not infunc:
         # Check to see if we're starting a function
         if x == ':':
	    infunc = 1
	    currentdef.append( x )
	 # EVERYTHING must be in a function; this ain't no scripting language!
	 else:
	    error( "Not in function" )
      # If we're in a func already...
      else:
         # Append the word to the current definition...
         currentdef.append( x )
	 # Check for a function terminator...
	 if x == ';':
	    # Append the current definition to the return list
	    final.append( currentdef )
	    # And reset it.
	    currentdef = []
   return final




# Does some word-changing to make assembly syntax match; + to add, - to sub,
# and so on.
# This is simply because NASM won't allow, say, '+' as a label.  Kinda
# irritating, actually...
def translatewords( words ):
   final = []
   transtable = {
   '+'   : 'addsig',
   '-'   : 'subsig',
   '*'   : 'mulsig',
   '/'   : 'divsig',
   '='   : 'equalsig',
   '<>'  : 'notequalsig',
   '>'   : 'greatersig',
   '<'   : 'lesssig',
   '>='  : 'greaterequalsig',
   '<='  : 'lessequalsig',
   '0='  : 'equalzerosig',
   '2/'  : 'twodivsig',
   '2*'  : 'twomulsig',
   '!'   : 'put',
   '@'   : 'get',
   'and' : 'andsig',
   'or'  : 'orsig',
   'd!'  : 'putdouble',
   'd@'  : 'getdouble',
   'c!'  : 'putchar',
   'c@'  : 'getchar',
   'u>'  : 'ugreater',
   'u<'  : 'uless',
   'u>=' : 'ugreaterequal',
   'u<=' : 'ulessequal'
   }
   for x in words:
      # If the word needs to be translated, do it.  Else, just stick it on.
      if transtable.has_key( x ):
         final.append( transtable[x] )
      else:
         final.append( x )
   return final


# This recognizes a compiler decleration (such as namespaces and global vars)
# and sticks it into the 'decl' global variable then returns the number
# of tokens that make up the decleration.
# Right now it only handles global variables
def handledecl( words )
   declargs = {
   "%%var" : 3           # Each variable decl has 2 args: a name and value.
   }                     # That is 3 tokens, including the decl itself
   title = words[0]
   # Check validity of the decl
   if not declargs.has_key( title ):
      error( "Unknown directive: " + title )
   body = words[: declargs[title] ]   # Grab the args
   body = body[1:]                 # Remove the title
   decls.append( (title, body) )   # Add decl to global var.
   return declargs[title]
   
      


# Pulls out all compiler declerations and stick them in a global var.
# Compiler declerations have the form of %%foo val1 val2 ...
def parsedecls( wordlist ):
   toskip = 0
   for x in range( len( wordlist) ):
      # Check if we need to skip any tokens.  You'll see why.
      if toskip > 0:
         toskip -= 1
	 continue
      if wordlist[x][:2] == '%%':
         # Okay.  If it's a decleration, we handle it.  handledecls() gets
	 # passed the next words, and returns the number of words
	 # that are part of the decleration.  We then skip those words.
         toskip = handledecl( wordlist[x:] )  



# Remove the block comments from a wordlist in the form of ( ... )
# Note that comment delimiters are words, and thus MUST be seperated by
# spaces!
def decomment( wordlist ):
   final = []
   incomment = 0
   for x in wordlist:
      # Check for startcomment
      if x == '(':
         incomment += 1
	 continue
      # Check for endcomment (they may be nested, unlike C /* ... */)
      elif x == ')':
         incomment -= 1
	 continue
      # If we're not in a comment, skip the work and continue
      if incomment == 0:
         final.append( x )
      # Make sure we don't get any mismatched comments!
      elif incomment < 0:
         error( "Mismatched comment!" )
   return final


# Remove line comments of the form \ ...\n (spaces are still important!)
# This also filters out newlines.  Bonus!  That means we don't have to ignore
# 'em later on.
def decomment2( wordlist ):
   final = []
   incomment = 0
   for x in wordlist:
      # Here comments can't be nested, so we just set the flag 1 or 0
      if x == '\\':
         incomment = 1
	 continue
      elif x == '\n':
         incomment = 0
	 continue
      if not incomment:
         final.append( x )
      # Should never happen.  ^_^
      elif incomment < 0:
         error( "Something impossible happened handling line comments" )
   return final

   

# Tokenize a string into a wordlist
# Tokenizing is insanely easy for Sig.  We just split at spaces.
# Newlines are tokens also, since they're needed for comments (see above)
def tokenize( s ):
   final = []
   a = string.split( s, ' ' )
   # Sometimes string.split leaves behind bunches of nasty empty strings,
   # which would probably do evil things to all the nice function-definition
   # func's above.  So we get rid of 'em.
   for x in a:
      if x == '':
         pass
      else:
         final.append( x )
   return final


# Do some gross translation to treat newlines as words for the comment code
# and tabs as spaces.
def translatetext( s ):
   final = ''
   for x in s:
      # We put spaces around newlines so they'll be treated as tokens
      if x == '\n':
         final += ' \n '
      # Turn tabs into whitespace
      elif x == '\t':
         final += ' '
      else:
         final += x

   return final


# Compiles the text of a file
# This just calls all the right functions in all the right order.
def compiletext( s ):
   s = translatetext( s )
   s = tokenize( s )
   s = decomment( s )
   s = decomment2( s )
   s = translatewords( s )
   s = findfuncdef( s )
   s = createfuncdefs( s )
   s = compfuncdefs( s )
   return s


###  TEST  ###
# Ignore this stuff; I wrote it while I was testing the parser.  If ye wanna
# understand more about this, try firing up the Python interprater, loading
# this file, and running 'a' through one step of the compiler at a time.

#a  = """
#( First we foo )
#: bop
#1 2 3 + *   \ Then we bar
#91 2/
#=           \ Finally, we bop.
#;
#
#( Then we baz )
#: baz
#1 9 4 - 2*
#35 = 24
#bop
#;
#"""
#a = translatetext( a )
#a = tokenize( a )
#a = decomment( a )
#a = decomment2( a )
#a = translatewords( a )
#a = findfuncdef( a )
#a = createfuncdefs( a )
