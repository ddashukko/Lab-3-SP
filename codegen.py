"""Генерація коду на цільовій мові (Python) з AST."""

HEADER = '''import sys
def _div(a, b):
    if isinstance(a, int) and isinstance(b, int):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q
    return a / b
def _mod(a, b):
    return a - b * _div(a, b)
def _print(*a):
    print(*a)
'''

class CodeGen:
    def __init__(self, prog):
        self.prog = prog
        self.lines = []
        self.globals = [d.value for d in prog.children if d.kind == "VarDecl"]
        self.types = {}

    def emit(self, s, lvl): self.lines.append("    " * lvl + s)

    def generate(self):
        self.lines = HEADER.splitlines() + [""]
        for d in self.prog.children:
            if d.kind == "VarDecl": self.stmt(d, 0)
        for d in self.prog.children:
            if d.kind == "FuncDef": self.func(d)
        self.emit("", 0)
        self.emit('if __name__ == "__main__":', 0)
        self.emit("main()", 1)
        return "\n".join(self.lines) + "\n"

    def func(self, d):
        params = ", ".join(p.value for p in d.children[0].children)
        self.emit("", 0)
        self.emit(f"def {d.value}({params}):", 0)
        if self.globals: self.emit("global " + ", ".join(self.globals), 1)
        n0 = len(self.lines)
        for s in d.children[1].children: self.stmt(s, 1)
        if len(self.lines) == n0 and not self.globals: self.emit("pass", 1)

    def body(self, n, lvl):
        n0 = len(self.lines)
        if n.kind == "Block":
            for s in n.children: self.stmt(s, lvl)
        else:
            self.stmt(n, lvl)
        if len(self.lines) == n0: self.emit("pass", lvl)

    def stmt(self, n, lvl):
        k = n.kind
        if k == "Block":
            for s in n.children: self.stmt(s, lvl)
        elif k == "VarDecl":
            t = n.attrs["type"]
            init = self.expr(n.children[0]) if n.children else "0"
            self.emit(f"{n.value} = {'int' if t=='int' else 'float'}({init})", lvl)
        elif k == "Assign":
            self.emit(f"{n.value} = {self.expr(n.children[0])}", lvl)
        elif k == "ExprStmt":
            self.emit(self.expr(n.children[0]), lvl)
        elif k == "If":
            self.emit(f"if {self.expr(n.children[0])}:", lvl)
            self.body(n.children[1], lvl + 1)
            if len(n.children) == 3:
                self.emit("else:", lvl)
                self.body(n.children[2], lvl + 1)
        elif k == "While":
            self.emit(f"while {self.expr(n.children[0])}:", lvl)
            self.body(n.children[1], lvl + 1)
        elif k == "For":
            init, cond, step, body = n.children
            if init.kind != "Empty": self.stmt(init, lvl)
            self.emit(f"while {self.expr(cond) if cond.kind != 'Empty' else 'True'}:", lvl)
            self.body(body, lvl + 1)
            if step.kind != "Empty": self.stmt(step, lvl + 1)
        elif k == "Return":
            self.emit("return" + (" " + self.expr(n.children[0]) if n.children else ""), lvl)
        elif k == "Print":
            self.emit("_print(" + ", ".join(self.expr(c) for c in n.children) + ")", lvl)

    def expr(self, n):
        k = n.kind
        if k == "Num": return repr(n.value)
        if k == "Str": return repr(n.value)
        if k == "Var": return n.value
        if k == "UnOp":
            e = self.expr(n.children[0])
            return f"(-{e})" if n.value == "-" else f"int(not {e})"
        if k == "Call": return f"{n.value}({', '.join(self.expr(a) for a in n.children)})"
        if k == "BinOp":
            a, b = self.expr(n.children[0]), self.expr(n.children[1])
            op = n.value
            if op == "/": return f"_div({a}, {b})"
            if op == "%": return f"_mod({a}, {b})"
            if op == "&&": return f"int(bool({a}) and bool({b}))"
            if op == "||": return f"int(bool({a}) or bool({b}))"
            if op in ("<", ">", "<=", ">=", "==", "!="): return f"int({a} {op} {b})"
            return f"({a} {op} {b})"
