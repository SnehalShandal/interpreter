import operator
BINARY_OPERATOR = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    'and': operator.and_,
    'or': operator.or_}
UNARY_OPERATOR = {
    '-': operator.neg,
    'not': operator.not_
}

DATA = []


class VarNotFound(Exception):
    pass


def is_variable(s):
    return s.isalpha()


def is_numeral(s):
    return s.isdigit()


def get_index(s):
    if is_numeral(s):
        num = int(s)
        for i, d in enumerate(DATA):
            if d == num:
                return i, num
        DATA.append(num)
        return len(DATA) - 1, num
    else:
        for i, d in enumerate(DATA):
            if type(d) is tuple and len(d) == 2 and d[0] == s:
                return i, DATA[d[1]]
        raise VarNotFound(f'Variable {s} is not defined')


def update_variable(var_name, value):
    value_index, _ = get_index(value)
    try:
        var_index, _ = get_index(var_name)
    except:
        DATA.append((var_name, value_index))
    else:
        DATA[var_index] = (var_name, value_index)


def interpret(line):
    li = line.split('\n')[0].split()

    variable_name = li.pop(0)
    assert is_variable(variable_name)
    assert li.pop(0) == '='

    if len(li) == 1:
        term = li.pop(0)
        assert is_numeral(term) or is_variable(term)
        _, result = get_index(term)
    elif len(li) == 2:
        op = li.pop(0)
        assert op in UNARY_OPERATOR
        term = li.pop(0)
        assert is_numeral(term) or is_variable(term)
        _, term_value = get_index(term)
        result = UNARY_OPERATOR[op](term_value)
    elif len(li) == 3:
        term1 = li.pop(0)
        assert is_numeral(term1) or is_variable(term1)
        op = li.pop(0)
        assert op in BINARY_OPERATOR
        term2 = li.pop(0)
        assert is_numeral(term2) or is_variable(term2)
        _, term_value1 = get_index(term1)
        _, term_value2 = get_index(term2)
        result = BINARY_OPERATOR[op](term_value1, term_value2)
    else:
        assert False, line

    update_variable(variable_name, str(result))


TYPE_ST_BLE = 'BLE'
TYPE_ST_BLT = 'BLT'
TYPE_ST_BE = 'BE'
TYPE_ST_B = 'B'
TYPE_ST_EXP = 'EXP'


INS_COUNTER = 0
class Instruction:
    def __init__(self, statement, addr=-1) -> None:
        # self.type_statement = type_statement
        self.statement = statement.strip()
        self.destination_addr = addr

        # Figuring out statement_type
        if not statement:
            self.statement_type = TYPE_ST_B
        elif not self.statement.startswith('while'):
            self.statement_type = TYPE_ST_EXP
        else:
            statement_li = self.statement.split('while')
            if len(statement_li) != 2:
                print("ERROR: Invalid while loop")
                exit(1)

            operand_str = statement_li[1]
            operand_str_li = operand_str.strip().split()
            if len(operand_str_li) != 3:
                print("ERROR: Invalid while condition")
                exit(1)

            op1, opr, op2 = operand_str_li
            op2 = op2.split(':')[0]

            if not is_variable(op1) and not is_numeral(op1):
                print("ERROR: Invalid operands for while condition")
                exit(1)
            if not is_variable(op2) and not is_numeral(op2):
                print("ERROR: Invalid operands for while condition")
                exit(1)

            if opr == '<':
                self.statement_type = TYPE_ST_BLT
                self.operand = [op1, op2]
            elif opr == '<=':
                self.statement_type = TYPE_ST_BLE
                self.operand = [op1, op2]
            elif opr == '>':
                self.statement_type = TYPE_ST_BLT
                self.operand = [op2, op1]
            elif opr == '>=':
                self.statement_type = TYPE_ST_BLE
                self.operand = [op2, op1]
            elif opr == '==':
                self.statement_type = TYPE_ST_BE
                self.operand = [op1, op2]
            else:
                print("ERROR")
                exit(1)

    def update_dest_addr(self, addr):
        self.destination_addr = addr

    def execute(self):
        global INS_COUNTER
        if self.statement_type == TYPE_ST_EXP:
            interpret(self.statement)
            INS_COUNTER += 1
        elif self.statement_type == TYPE_ST_BLE:
            _, op1_value = get_index(self.operand[0])
            _, op2_value = get_index(self.operand[1])
            if not (op1_value <= op2_value):
                INS_COUNTER = self.destination_addr
            else:
                INS_COUNTER += 1
        elif self.statement_type == TYPE_ST_BLT:
            _, op1_value = get_index(self.operand[0])
            _, op2_value = get_index(self.operand[1])
            if not(op1_value < op2_value):
                INS_COUNTER = self.destination_addr
            else:
                INS_COUNTER += 1
        elif self.statement_type == TYPE_ST_BLE:
            _, op1_value = get_index(self.operand[0])
            _, op2_value = get_index(self.operand[1])
            if op1_value != op2_value:
                INS_COUNTER = self.destination_addr
            else:
                INS_COUNTER += 1
        elif self.statement_type == TYPE_ST_B:
            INS_COUNTER = self.destination_addr
    def __str__(self) -> str:
        statement = self.statement
        if self.statement_type != TYPE_ST_EXP:
            statement = f'{self.operand[0]} {self.operand[1]}'
        return f'{self.statement_type}:{statement}->{self.destination_addr}'


CURR_TAB_COUNTER = 0
INDENT_START_INDEXES = []
INS_LIST = []
BRANCH_U_COUNTER = 0

with open('input.txt') as fp:
    data = fp.readlines()

for i, record in enumerate(data):
    tabs = 0
    while record[tabs] == '\t':
        tabs += 1

    if tabs == CURR_TAB_COUNTER + 1:
        CURR_TAB_COUNTER = tabs
        INDENT_START_INDEXES.append(i - 1)
    elif tabs + 1 == CURR_TAB_COUNTER:
        CURR_TAB_COUNTER = tabs
        indent_start = INDENT_START_INDEXES.pop()

        INS_LIST.append(Instruction('', indent_start))
        BRANCH_U_COUNTER += 1

        INS_LIST[indent_start].update_dest_addr(BRANCH_U_COUNTER + i)
    elif tabs == CURR_TAB_COUNTER:
        pass
    else:
        print("ERROR")
        exit(1)

    record_str = record.strip()
    INS_LIST.append(Instruction(record_str))

while INS_COUNTER < len(INS_LIST):
    a = INS_LIST[INS_COUNTER]
    a.execute()

variable_values = []
garbage_values = [True] * len(DATA)

for i, record in enumerate(DATA):
    if type(record) == tuple:
        garbage_values[i] = False
        variable_name = record[0]
        value_index = record[1]
        garbage_values[value_index] = False
        value = DATA[value_index]
        variable_values.append((variable_name, value))

print(DATA)

print('Variable values are:')
for record in variable_values:
    print(record[0], record[1])

print('Garbage values are:')
for i, value in enumerate(garbage_values):
    if value:
        print(DATA[i])

