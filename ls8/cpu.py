"""CPU functionality."""

import sys

instruction_codes = {
    'hlt': '0x1',
    'ldi': '0x82',
    'prn': '0x47',
    'add': '0xa0',
    'mul': '0xa2',
    'push': '0x45',
    'pop': '0x46',
    'call': '0x50',
    'ret': '0x11'
}

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0xf4 if (i == 7) else 0 for i in range(0, 8)]
        self.ram = [0] * 256
        self.running = True
        self.branchtable = {}
        self.branchtable[instruction_codes['hlt']] = self.handle_hlt
        self.branchtable[instruction_codes['ldi']] = self.handle_ldi
        self.branchtable[instruction_codes['prn']] = self.handle_prn
        self.branchtable[instruction_codes['add']] = self.handle_add
        self.branchtable[instruction_codes['mul']] = self.handle_mul
        self.branchtable[instruction_codes['push']] = self.handle_push
        self.branchtable[instruction_codes['pop']] = self.handle_pop
        self.branchtable[instruction_codes['call']] = self.handle_call
        self.branchtable[instruction_codes['ret']] = self.handle_ret


    def ram_read(self, mar): # mar - [_Memory Address Register_]
        return self.ram[mar]

    def ram_write(self, mar, mdr): # mar - [_Memory Address Register_] | mdr - [_Memory Data Register_]
        self.ram[mar] = mdr

    def stack_push(self, val):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = val

    def stack_pop(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram[self.reg[7]]
        self.reg[7] += 1

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []

        with open(sys.argv[1], 'r') as f:
            for l in f.readlines():
                if l:
                    line_list = [s.strip() for s in l.split('#')]
                    nums = '01'
                    for s in line_list:
                        if (s) and (s[0] in nums) and (s[-1] in nums):
                            program.append(bin(int(s, 2)))
            # print(program)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram[address] = int(instruction, 2)
            address += 1
        # print(self.ram)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 'ADD':
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_hlt(self): # HLT - stop running the program
        self.pc += 1
        self.running = False

    def handle_ldi(self): # LDI - set the value of a register to an integer
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def handle_prn(self): # PRN - print value stored in given register
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def handle_add(self):
        self.alu('ADD', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc += 3

    def handle_mul(self): # MUL - multiply values in two registers together and store the result in registerA
        self.alu('MUL', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc += 3

    def handle_push(self): # PUSH - push the value in the given register on the stack
        # self.reg[7] -= 1
        # self.ram[self.reg[7]] = self.reg[self.ram_read(self.pc + 1)]
        self.stack_push(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def handle_pop(self): # POP - pop the value at the top of the stack into the given register
        # self.reg[self.ram_read(self.pc + 1)] = self.ram[self.reg[7]]
        # self.reg[7] += 1
        self.stack_pop()
        self.pc += 2

    def handle_call(self):
        # self.reg[7] -= 1
        # self.ram[self.reg[7]] = (self.pc + 2)
        self.stack_push(self.pc + 2)
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def handle_ret(self):
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = hex(self.ram[self.pc]) # ir - [_Instruction Register_]
            self.branchtable[ir]()

        # running = True
        # while running:
        #     ir = self.ram[self.pc] # ir - [_Instruction Register_]
        #     # operand_a = self.ram_read(self.pc + 1)
        #     # operand_b = self.ram_read(self.pc + 2)
        #     if hex(ir) == '0x1': # HLT - stop running the program
        #         running = False
        #         self.pc += 1
        #     elif hex(ir) == '0x82': # LDI - set the value of a register to an integer
        #         reg_slot = self.ram_read(self.pc + 1)
        #         self.reg[reg_slot] = self.ram_read(self.pc + 2)
        #         self.pc += 3
        #     elif hex(ir) == '0x47': # PRN - print value stored in given register
        #         print(self.reg[self.ram_read(self.pc + 1)])
        #         self.pc += 2
        #     elif hex(ir) == '0xa2': # MUL - multiply values in two registers together and store the result in registerA
        #         self.alu('MUL', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        #         self.pc += 3

# x = CPU()
# x.load() # examples/print8.ls8
