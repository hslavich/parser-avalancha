class Postcondition():
    def __init__(self, post, fun):
        self.post = post
        self.fun = fun

    def compile(self):
        return '''
void post_{id}({0}) {{
    // {post!r}
}}
'''.format(self.fun.params(True), id = self.fun.id, post=self.post)
