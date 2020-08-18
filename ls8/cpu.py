"""CPU functionality."""

import sys

# '0x1': # HLT
# '0x82': # LDI
# '0x47': # PRN
# '0xa2': # MUL

instruction_codes = {
    'hlt': '0x1',
    'ldi': '0x82',
    'prn': '0x47',
    'mul': '0xa2'
}

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.running = True
        self.branchtable = {}
        self.branchtable[instruction_codes['hlt']] = self.handle_hlt
        self.branchtable[instruction_codes['ldi']] = self.handle_ldi
        self.branchtable[instruction_codes['prn']] = self.handle_prn
        self.branchtable[instruction_codes['mul']] = self.handle_mul


    def ram_read(self, mar): # mar - [_Memory Address Register_]
        return self.ram[mar]

    def ram_write(self, mar, mdr): # mar - [_Memory Address Register_] | mdr - [_Memory Data Register_]
        self.ram[mar] = mdr

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
        # reg_slot = self.ram_read(self.pc + 1)
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def handle_prn(self): # PRN - print value stored in given register
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def handle_mul(self): # MUL - multiply values in two registers together and store the result in registerA
        self.alu('MUL', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc += 3

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
