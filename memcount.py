#!/usr/bin/python

import sys
from elftools.elf.elffile import ELFFile
from multiverse import Rewriter
from x64_assembler import _asm

guidance = {}

entry_point = 0
global_addr = 0

'''
    Count memory instructions. This uses a global list of memory instructions
    for reference.
'''
def count_instruction(inst): 
    #
    # Explanation:
    # 32bit system does not have a quad-word or 8-byte reference. Thus we only
    # have double-word (dword) or 4-byte addressable memory. But down below
    # at 'rewriter.alloc_globals` we reserved 8-bytes of global space for this
    # counter. Thus, this is a 'hack' to accumulate the count a 4-byte space
    # and let it overflow into the other 4-byte space
    #
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

    # If this address is not in the guidance then return no instrumentation
    if not inst.address in guidance:
        return None

    inc = increment_template%( global_addr, global_addr+4 )
    return _asm( inc )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Error: must pass executable filename.\nCorrect usage: %s <filename>" % sys.argv[0]
        sys.exit()

    with open("units_guidance.txt") as f:
        for line in f:
            guidance[int(line, 16)] = True

    f = open(sys.argv[1])
    e = ELFFile(f)
    entry_point = e.header.e_entry
    f.close()

    rewriter = Rewriter(False,True,False)
    global_addr = rewriter.alloc_globals(8,'x86') #8 bytes
    print("Count Address: " + str(hex(global_addr)))
    rewriter.set_before_inst_callback(count_instruction)
    rewriter.rewrite(sys.argv[1],'x86')

