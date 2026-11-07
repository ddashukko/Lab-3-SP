"""Семантичний аналіз: таблиця символів, перевірка оголошень та викликів."""

class SemanticError(Exception): pass

def check(prog):
    funcs, errors = {}, []
    for d in prog.children:
        if d.kind == "FuncDef":
            if d.value in funcs:
                errors.append(f"Рядок {d.line}: функцію {d.value} вже оголошено")
            funcs[d.value] = d
    if "main" not in funcs:
        errors.append("Відсутня функція main")

    def walk(n, scopes):
        k = n.kind
        if k == "FuncDef":
            scopes = scopes + [{p.value: p.attrs["type"] for p in n.children[0].children}]
            walk(n.children[1], scopes); return
        if k == "Block":
            scopes = scopes + [{}]
            for c in n.children: walk(c, scopes)
            return
        if k == "For":  # окрема область видимості не потрібна, але init бачить scope
            scopes = scopes + [{}]
            for c in n.children: walk(c, scopes)
            return
        if k == "VarDecl":
            for c in n.children: walk(c, scopes)
            if n.value in scopes[-1]:
                errors.append(f"Рядок {n.line}: змінну {n.value} вже оголошено")
            scopes[-1][n.value] = n.attrs["type"]; return
        if k in ("Var", "Assign"):
            if not any(n.value in s for s in scopes):
                errors.append(f"Рядок {n.line}: змінна {n.value} не оголошена")
        if k == "Call":
            f = funcs.get(n.value)
            if f is None:
                errors.append(f"Рядок {n.line}: функція {n.value} не оголошена")
            elif len(f.children[0].children) != len(n.children):
                errors.append(f"Рядок {n.line}: {n.value} очікує {len(f.children[0].children)} арг., передано {len(n.children)}")
        for c in n.children: walk(c, scopes)

    glob = {}
    for d in prog.children:
        if d.kind == "VarDecl":
            walk(d, [glob])
    for d in prog.children:
        if d.kind == "FuncDef":
            walk(d, [glob])
    if errors:
        raise SemanticError("\n".join(errors))
