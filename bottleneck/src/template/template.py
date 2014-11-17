import os
import re
import ast


def make_pyx():
    template('reduce.pyx')


def template(template_filename):

    dirpath = os.path.dirname(__file__)
    filename = os.path.join(dirpath, template_filename)
    with open(filename, 'r') as f:
        src_str = f.read()

    src = expand_functions(src_str)

    filename = os.path.join(dirpath, '..', 'auto_pyx', template_filename)
    with open(filename, 'w') as f:
        f.write(src)


def expand_functions(src_str):
    FUNC = r'^def|cdef'
    DTYPE = r'\s*#\s*bn.dtypes\s*=\s*'
    src_list = []
    lines = src_str.splitlines()
    nlines = len(lines)
    i = 0
    while i < nlines:
        line = lines[i]
        if re.match(FUNC, line):
            dtypes = []
            func_list = [line]
            i += 1
            while True:
                if i >= nlines:
                    line = '\n'.join(func_list)
                    break
                line = lines[i]
                if re.match(DTYPE, line):
                    dtypes = re.sub(DTYPE, '', line)
                    dtypes = ast.literal_eval(dtypes)
                    line = None
                elif re.match(FUNC, line):
                    i -= 1
                    func_str = '\n'.join(func_list)
                    line = expand_dtypes(func_str, dtypes)
                    break
                else:
                    if line is not None:
                        func_list.append(line)
                i += 1
        src_list.append(line)
        i += 1
    src = '\n'.join(src_list)
    return src


def expand_dtypes(func_str, dtypes):
    DTYPE = 'DTYPE'
    if DTYPE not in func_str:
        return func_str
    func_list = []
    for dtype in dtypes:
        f = func_str[:]
        for i, dt in enumerate(dtype):
            f = f.replace('DTYPE%d' % i, dt)
            func_list.append(f)
    return '\n'.join(func_list)


if __name__ == '__main__':
    make_pyx()
