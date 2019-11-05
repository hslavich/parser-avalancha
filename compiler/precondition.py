class Precondition():
    def __init__(self, pre, fun):
        self.pre = pre
        self.fun = fun

    def compile(self):
        return '''
void pre_{id}({0}) {{
    // TODO: precondicion
}}
'''.format(self.fun.params(), id = self.fun.id)
