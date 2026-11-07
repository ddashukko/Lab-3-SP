"""Синтаксичний аналізатор (аналог YACC, LALR(1)) -> AST."""
import ply.yacc as yacc
from lexer import tokens, make_lexer
from ast_nodes import Node

# Пріоритети й асоціативність: вирішують shift/reduce конфлікти
precedence = (
    ("nonassoc", "IFX"),      # if без else
    ("nonassoc", "ELSE"),     # else має вищий пріоритет -> SHIFT (dangling else)
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQ", "NE"),
    ("left", "LT", "GT", "LE", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "UMINUS", "NOT"),
)

class ParseError(Exception): pass

def p_program(p):
    "program : external_list"
    p[0] = Node("Program", children=p[1])

def p_external_list(p):
    """external_list : external_list external
                     | external"""
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_external(p):
    """external : func_def
                | var_decl"""
    p[0] = p[1]

def p_type(p):
    """type : INT
            | FLOAT
            | VOID"""
    p[0] = p[1]

def p_func_def(p):
    "func_def : type ID LPAREN params_opt RPAREN block"
    p[0] = Node("FuncDef", p[2], [Node("Params", children=p[4]), p[6]], p.lineno(2), ret=p[1])

def p_params_opt(p):
    """params_opt : params
                  | empty"""
    p[0] = p[1] or []

def p_params(p):
    """params : params COMMA param
              | param"""
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_param(p):
    "param : type ID"
    p[0] = Node("Param", p[2], line=p.lineno(2), type=p[1])

def p_empty(p):
    "empty :"
    p[0] = None

def p_block(p):
    "block : LBRACE stmt_list RBRACE"
    p[0] = Node("Block", children=p[2], line=p.lineno(1))

def p_stmt_list(p):
    """stmt_list : stmt_list stmt
                 | empty"""
    p[0] = (p[1] + [p[2]]) if len(p) == 3 else []

def p_stmt(p):
    """stmt : var_decl
            | simple_stmt SEMI
            | if_stmt
            | while_stmt
            | for_stmt
            | return_stmt
            | print_stmt
            | block"""
    p[0] = p[1]

def p_var_decl(p):
    """var_decl : type ID SEMI
                | type ID ASSIGN expr SEMI"""
    p[0] = Node("VarDecl", p[2], [p[4]] if len(p) == 6 else [], p.lineno(2), type=p[1])

def p_simple_stmt_assign(p):
    "simple_stmt : ID ASSIGN expr"
    p[0] = Node("Assign", p[1], [p[3]], p.lineno(1))

def p_simple_stmt_expr(p):
    "simple_stmt : expr"
    p[0] = Node("ExprStmt", children=[p[1]], line=p.lineno(1))

# --- shift/reduce: "dangling else" вирішується через %prec ---
def p_if_stmt(p):
    "if_stmt : IF LPAREN expr RPAREN stmt %prec IFX"
    p[0] = Node("If", children=[p[3], p[5]], line=p.lineno(1))

def p_if_else_stmt(p):
    "if_stmt : IF LPAREN expr RPAREN stmt ELSE stmt"
    p[0] = Node("If", children=[p[3], p[5], p[7]], line=p.lineno(1))

def p_while_stmt(p):
    "while_stmt : WHILE LPAREN expr RPAREN stmt"
    p[0] = Node("While", children=[p[3], p[5]], line=p.lineno(1))

def p_for_stmt(p):
    "for_stmt : FOR LPAREN for_init SEMI expr_opt SEMI simple_opt RPAREN stmt"
    E = lambda x: x if x is not None else Node("Empty")
    p[0] = Node("For", children=[E(p[3]), E(p[5]), E(p[7]), p[9]], line=p.lineno(1))

def p_for_init(p):
    """for_init : simple_stmt
                | type ID ASSIGN expr
                | empty"""
    if len(p) == 5:
        p[0] = Node("VarDecl", p[2], [p[4]], p.lineno(2), type=p[1])
    else:
        p[0] = p[1]

def p_simple_opt(p):
    """simple_opt : simple_stmt
                  | empty"""
    p[0] = p[1]

def p_expr_opt(p):
    """expr_opt : expr
                | empty"""
    p[0] = p[1]

def p_return_stmt(p):
    """return_stmt : RETURN SEMI
                   | RETURN expr SEMI"""
    p[0] = Node("Return", children=[p[2]] if len(p) == 4 else [], line=p.lineno(1))

def p_print_stmt(p):
    "print_stmt : PRINT LPAREN args_opt RPAREN SEMI"
    p[0] = Node("Print", children=p[3], line=p.lineno(1))

def p_binop(p):
    """expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr MOD expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr
            | expr EQ expr
            | expr NE expr
            | expr AND expr
            | expr OR expr"""
    p[0] = Node("BinOp", p[2], [p[1], p[3]], p.lineno(2))

def p_unary(p):
    """expr : MINUS expr %prec UMINUS
            | NOT expr"""
    p[0] = Node("UnOp", p[1], [p[2]], p.lineno(1))

def p_paren(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]

def p_int(p):
    "expr : INT_LIT"
    p[0] = Node("Num", p[1], line=p.lineno(1), type="int")

def p_float(p):
    "expr : FLOAT_LIT"
    p[0] = Node("Num", p[1], line=p.lineno(1), type="float")

def p_string(p):
    "expr : STRING"
    p[0] = Node("Str", p[1], line=p.lineno(1))

def p_var(p):
    "expr : ID"
    p[0] = Node("Var", p[1], line=p.lineno(1))

def p_call(p):
    "expr : ID LPAREN args_opt RPAREN"
    p[0] = Node("Call", p[1], p[3], p.lineno(1))

def p_args_opt(p):
    """args_opt : args
                | empty"""
    p[0] = p[1] or []

def p_args(p):
    """args : args COMMA expr
            | expr"""
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_error(p):
    if p is None:
        raise ParseError("Несподіваний кінець файлу")
    raise ParseError(f"Рядок {p.lineno}: синтаксична помилка біля {p.value!r}")

def parse(src, debug=False):
    lexer = make_lexer()
    lexer.lineno = 1
    parser = yacc.yacc(debug=debug, write_tables=False, debugfile="parser.out",
                       errorlog=yacc.NullLogger() if not debug else yacc.PlyLogger(__import__("sys").stderr))
    return parser.parse(src, lexer=lexer, tracking=True)
