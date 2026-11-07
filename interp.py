"""Обчислення (інтерпретація AST)."""

class Return(Exception):
    def __init__(self, v): self.v = v

class Env:
    def __init__(self, parent=None):
        self.vars, self.parent = {}, parent
    def find(self, n):
        e = self
        while e:
            if n in e.vars: return e
            e = e.parent
        raise NameError(n)

def coerce(t, v):
    return int(v) if t == "int" else float(v) if t == "float" else v

def cdiv(a, b):
    if b == 0: raise ZeroDivisionError("ділення на нуль")
    if isinstance(a, int) and isinstance(b, int):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q
    return a / b

def cmod(a, b):
    return a - b * cdiv(a, b)

BIN = {
    "+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b,
    "/": cdiv, "%": cmod,
    "<": lambda a, b: int(a < b), ">": lambda a, b: int(a > b),
    "<=": lambda a, b: int(a <= b), ">=": lambda a, b: int(a >= b),
    "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b),
}

class Interpreter:
    def __init__(self, prog, out=print):
        self.funcs = {d.value: d for d in prog.children if d.kind == "FuncDef"}
        self.glob = Env()
        self.out = out
        for d in prog.children:
            if d.kind == "VarDecl": self.exec(d, self.glob)

    def run(self):
        return self.call("main", [])

    def call(self, name, args):
        f = self.funcs[name]
        env = Env(self.glob)
        for p, a in zip(f.children[0].children, args):
            env.vars[p.value] = (p.attrs["type"], coerce(p.attrs["type"], a))
        try:
            self.exec(f.children[1], env)
        except Return as r:
            return coerce(f.attrs["ret"], r.v) if r.v is not None else None
        return None

    def exec(self, n, env):
        k = n.kind
        if k == "Block":
            e = Env(env)
            for s in n.children: self.exec(s, e)
        elif k == "VarDecl":
            t = n.attrs["type"]
            env.vars[n.value] = (t, coerce(t, self.ev(n.children[0], env)) if n.children else 0)
        elif k == "Assign":
            e = env.find(n.value); t = e.vars[n.value][0]
            e.vars[n.value] = (t, coerce(t, self.ev(n.children[0], env)))
        elif k == "ExprStmt":
            self.ev(n.children[0], env)
        elif k == "If":
            if self.ev(n.children[0], env): self.exec(n.children[1], env)
            elif len(n.children) == 3: self.exec(n.children[2], env)
        elif k == "While":
            while self.ev(n.children[0], env): self.exec(n.children[1], env)
        elif k == "For":
            init, cond, step, body = n.children
            env = Env(env)
            if init.kind != "Empty": self.exec(init, env)
            while cond.kind == "Empty" or self.ev(cond, env):
                self.exec(body, env)
                if step.kind != "Empty": self.exec(step, env)
        elif k == "Return":
            raise Return(self.ev(n.children[0], env) if n.children else None)
        elif k == "Print":
            self.out(" ".join(str(self.ev(c, env)) for c in n.children))

    def ev(self, n, env):
        k = n.kind
        if k == "Num" or k == "Str": return n.value
        if k == "Var":
            return env.find(n.value).vars[n.value][1]
        if k == "UnOp":
            v = self.ev(n.children[0], env)
            return -v if n.value == "-" else int(not v)
        if k == "BinOp":
            if n.value == "&&":
                return int(bool(self.ev(n.children[0], env)) and bool(self.ev(n.children[1], env)))
            if n.value == "||":
                return int(bool(self.ev(n.children[0], env)) or bool(self.ev(n.children[1], env)))
            return BIN[n.value](self.ev(n.children[0], env), self.ev(n.children[1], env))
        if k == "Call":
            return self.call(n.value, [self.ev(a, env) for a in n.children])
        raise RuntimeError(f"невідомий вузол {k}")
