# General

The following are guidelines for getting Multiverse up and running from a 
cloned repository. This information isn't compiled anywhere else, so look here
first.

Multiverse uses python2.7 and pip. Make sure you're not using python3 and pip3.
You must be running on a 64bit platform as Pwntools does not support 32bit
python regardless of it supporting rewriting/using 32bit binaries.

All 'recompiled' binaries must be ran with the LD_BIND_NOW=1 environment
variable, e.g.:

    LD_BIND_NOW=1 ./simplest32-r

## Installation

### Pwntools and ELFManip

Install pwntools like (pwntools installs pyelftools):

    pip install pwntools

Clone the [ELFManip Repo](https://github.com/schieb/ELFManip) and install
with:

    sudo python setup.py install

### Capstone

First, make sure there is no capstone egg installed in pip:

    pip uninstall capstone

Then you must use the following capstone repo
[https://github.com/baumane/capstone](https://github.com/baumane/capstone) to
build capstone. Compile with the following commands to get the mutliverse to
work:

    CAPSTONE_ARCHS="aarch64 x86" CAPSTONE_USE_SYS_DYN_MEM=yes CAPSTONE_DIET=no CAPSTONE_X86_REDUCE=no ./make.sh
    sudo CAPSTONE_ARCHS="aarch64 x86" CAPSTONE_USE_SYS_DYN_MEM=yes CAPSTONE_DIET=no CAPSTONE_X86_REDUCE=no ./make.sh install

After this travel to bindings/python and run:

    sudo python setup.py install

This should be all one needs to do for capstone in particular.

### Minor edits

Make the following edits to the source tree.

Getting Pwntools to work with 32bit from [Issue 2](https://github.com/utds3lab/multiverse/issues/2):

    diff --git a/x86_assembler.py b/x86_assembler.py
    index 3571864..63b8471 100644
    --- a/x86_assembler.py
    +++ b/x86_assembler.py
    @@ -1,5 +1,5 @@
     import pwn
    -pwn.context(os='linux',arch='i386')
    +pwn.context(os='linux',arch='i386',bits=32)
     import re
     import struct

Letting the 'instrumentation' files work with 32bit binaries:

    diff --git a/icount.py b/icount.py
    index 062ca2f..403ada9 100644
    --- a/icount.py
    +++ b/icount.py
    @@ -38,8 +38,11 @@ if __name__ == '__main__':
         entry_point = e.header.e_entry
         f.close()
         rewriter = Rewriter(False,True,False)
    -    global_addr = rewriter.alloc_globals(8,'x86-64') #8 bytes
    +    #global_addr = rewriter.alloc_globals(8,'x86-64') #8 bytes
    +    #rewriter.set_before_inst_callback(count_instruction)
    +    #rewriter.rewrite(sys.argv[1],'x86-64')
    +    global_addr = rewriter.alloc_globals(8,'x86') #8 bytes
         rewriter.set_before_inst_callback(count_instruction)
    -    rewriter.rewrite(sys.argv[1],'x86-64')
    +    rewriter.rewrite(sys.argv[1],'x86')
       else:
         print "Error: must pass executable filename.\nCorrect usage: %s <filename>"%sys.argv[0]
    
