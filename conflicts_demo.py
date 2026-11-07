"""Демонстрація конфліктів LALR: запустіть `python3 conflicts_demo.py` і дивіться повідомлення PLY.
1) E : E '+' E  без пріоритетів -> shift/reduce (YACC за замовчуванням обирає SHIFT)
2) reduce/reduce: A і B виводять одне й те саме (YACC обирає правило, що йде ПЕРШИМ у граматиці)"""
import sys, ply.lex as lex, ply.yacc as yacc
tokens = ("NUM", "PLUS", "X")
t_PLUS, t_NUM, t_X = r"\+", r"\d+", r"x"
def t_error(t): t.lexer.skip(1)

def p_s(p):
    """s : e
         | a
         | b"""
def p_e(p):
    """e : e PLUS e
         | NUM"""                 # shift/reduce: 1+2+3 -> (1+2)+3 чи 1+(2+3)?
def p_a(p): "a : X"              # reduce/reduce: після X можна звести і до a, і до b
def p_b(p): "b : X"
def p_error(p): pass

print("=== Конфлікти (без precedence) ===", file=sys.stderr)
yacc.yacc(debug=True, write_tables=False, debugfile="conflicts.out")
