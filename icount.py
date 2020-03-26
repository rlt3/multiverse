#!/usr/bin/python

import sys
from elftools.elf.elffile import ELFFile
from multiverse import Rewriter
from x64_assembler import _asm
#from x86_assembler import _asm

global_addr = 0
count = 0

'''
  This counts the number of instructions in a 32-bit binary with an 8-byte counter.
  The counter is not printed at the end of execution, so a breakpoint must be set
  with a debugger and the value of the counter must be manually verified.
  While the assembly was originally written to work with 32-bit binaries, it also
  works for 64-bit binaries, although it is less efficient than it needs to be.
  Right now, this is configured to rewrite 64-bit binaries, although it can be
  easily modified to rewrite 32-bit binaries.
'''
def count_instruction(inst): 
    global global_addr
    global count
    increment_template = '''
    push ax
    lahf
    seto al
    add DWORD PTR [0x%x],1
    adc DWORD PTR [0x%x],0
    cmp al,0x81
    sahf
    pop ax
    '''
    inc = increment_template % (global_addr, global_addr+4)
    if count == 0:
      count = count + 1
      print(inc)
    return _asm(inc)
    #increment_template = '''
    #add QWORD PTR [0x%x],1
    #'''
    #inc = increment_template % (global_addr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Error: must pass executable filename.\nCorrect usage: %s <filename>" % sys.argv[0]
        sys.exit(1)
    rewriter = Rewriter(False,True,False)
    global_addr = rewriter.alloc_globals(8,'x86-64') #8 bytes
    rewriter.set_before_inst_callback(count_instruction)
    rewriter.rewrite(sys.argv[1],'x86-64')
    print("Count Address: " + str(hex(global_addr)))
    #rewriter.rewrite(sys.argv[1],'x86')
