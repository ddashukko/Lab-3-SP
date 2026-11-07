#!/usr/bin/env python3
"""MiniC: лексер + LALR-парсер (PLY) -> AST -> семантика -> інтерпретація / генерація Python / візуалізація."""
import argparse, io, json, sys, contextlib
from lexer import make_lexer
from parser import parse, ParseError
from semantic import check, SemanticError
from interp import Interpreter
from codegen import CodeGen
import os

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--tokens", action="store_true", help="вивести токени")
    ap.add_argument("--ast", action="store_true", help="вивести AST текстом")
    ap.add_argument("--run", action="store_true", help="виконати програму (обчислення)")
    ap.add_argument("--py", metavar="OUT.py", help="згенерувати код на Python")
    ap.add_argument("--html", metavar="OUT.html", help="візуалізація AST (d3.js)")
    ap.add_argument("--debug", action="store_true", help="записати parser.out (таблиці LALR, конфлікти)")
    a = ap.parse_args()
    src = open(a.file, encoding="utf-8").read()

    if a.tokens:
        lx = make_lexer(); lx.input(src)
        for t in lx: print(t.lineno, t.type, repr(t.value))
    try:
        ast = parse(src, debug=a.debug)
        check(ast)
    except (ParseError, SemanticError) as e:
        print("Помилка:", e, file=sys.stderr); sys.exit(1)
    if a.ast: print(ast.dump())

    buf = []
    if a.run or a.html:
        it = Interpreter(ast, out=(print if a.run else buf.append))
        if a.html:
            it.out = buf.append
        it.run()
    py = CodeGen(ast).generate()
    if a.py:
        open(a.py, "w", encoding="utf-8").write(py)
        print(f"Python-код записано у {a.py}")
    if a.html:

        tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "viz_template.html"),
                   encoding="utf-8").read()
        data = {"ast": ast.to_dict(), "source": src, "output": "\n".join(buf), "python": py}
        open(a.html, "w", encoding="utf-8").write(
            tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
        print(f"Візуалізацію записано у {a.html}")

if __name__ == "__main__":
    main()
