import operator
BINARY_OPERATOR = {
    '+': operator.add,
    '−': operator.sub,
    '∗': operator.mul,
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

with open('input.txt') as fp:
    data = fp.readlines()

for record in data:
    interpret(record)


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
