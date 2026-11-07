"""Лексичний аналізатор (аналог Lex)."""
import ply.lex as lex

reserved = {
    "int": "INT", "float": "FLOAT", "void": "VOID", "if": "IF", "else": "ELSE",
    "while": "WHILE", "for": "FOR", "return": "RETURN", "print": "PRINT",
}

tokens = ["ID", "INT_LIT", "FLOAT_LIT", "STRING",
          "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
          "LT", "GT", "LE", "GE", "EQ", "NE", "AND", "OR", "NOT", "ASSIGN",
          "LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMI", "COMMA"] + list(reserved.values())

t_PLUS, t_MINUS, t_TIMES, t_DIVIDE, t_MOD = r"\+", r"-", r"\*", r"/", r"%"
t_LE, t_GE, t_EQ, t_NE, t_AND, t_OR = r"<=", r">=", r"==", r"!=", r"&&", r"\|\|"
t_LT, t_GT, t_NOT, t_ASSIGN = r"<", r">", r"!", r"="
t_LPAREN, t_RPAREN, t_LBRACE, t_RBRACE = r"\(", r"\)", r"\{", r"\}"
t_SEMI, t_COMMA = r";", r","
t_ignore = " \t\r"

def t_COMMENT(t):
    r"//[^\n]*|/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")

def t_FLOAT_LIT(t):
    r"\d+\.\d+"
    t.value = float(t.value); return t

def t_INT_LIT(t):
    r"\d+"
    t.value = int(t.value); return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]; return t

def t_ID(t):
    r"[A-Za-z_][A-Za-z_0-9]*"
    t.type = reserved.get(t.value, "ID"); return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

class LexError(Exception): pass

def t_error(t):
    raise LexError(f"Рядок {t.lineno}: недопустимий символ {t.value[0]!r}")

def make_lexer():
    return lex.lex()
