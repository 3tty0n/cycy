import os

from cycy import bytecode, compiler
from cycy.objects import W_Char
from cycy.parser import ast
from cycy.parser.sourceparser import parse

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, purefunction
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
        def can_enter_jit(self,**kw): pass
    def purefunction(f): return f

def get_location(pc):
    return "%s" % pc

jitdriver = JitDriver(greens=['pc'], reds=['byte_code'],
        get_printable_location=get_location)

class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def __init__(self):
        self.compiled_functions = {}

    def run_main(self):
        main_byte_code = self.compiled_functions["main"]
        self.run(main_byte_code)

    def run(self, byte_code):
        pc = 0
        while pc < len(byte_code.instructions):
            jitdriver.jit_merge_point(pc=pc, byte_code=byte_code)

            opcode = byte_code.instructions[pc]
            arg = byte_code.instructions[pc + 1]
            pc += 2

            if opcode == bytecode.PUTC:
                value = byte_code.constants[arg]
                assert isinstance(value, W_Char)
                os.write(1, value.str())
                # TODO: error handling?


def interpret(source):
    interp = CyCy()
    program = parse(source)

    assert isinstance(program, ast.Program)
    for function in program.functions:
        assert isinstance(function, ast.Function)
        byte_code = compiler.compile(function)
        interp.compiled_functions[function.name] = byte_code

    interp.run_main()
    # TODO: duh, this should really come from the program
    return 5
