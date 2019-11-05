class Postcondition():
    def __init__(self, post, fun):
        self.post = post
        self.fun = fun

    def compile(self):
        return '''
void post_{id}({0}, Term* res) {{
    // TODO: postcondicion
}}
'''.format(self.fun.params(), id = self.fun.id)
