import ply.lex as lex


class BltLexer:
    tokens = (
        "NUMBER",
        "MINUS",  # skipped ranking
        "EQUALS",  # overvote indicator
        "ZERO",  # standalone zero (end of ballots)
        "BALLOT_END",  # same as ZERO (optional separate name)
        "LPAR",  # left double quote (")
        "RPAR",  # right double quote (")
        "STRING",  # quoted candidate names or title
        "NEWLINE",
        "COMMENT",
    )

    t_ignore: str = " \t"  # Ignore spaces and tabs

    # Simple tokens
    t_MINUS: str = r"-"
    t_EQUALS: str = r"="
    t_ZERO: str = r"0"

    # Integers
    def t_NUMBER(self, t):
        r"[1-9][0-9]*"
        t.value = int(t.value)
        return t

    # Newlines
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # Comments (ignore after #)
    def t_COMMENT(self, t):
        r"\#.*"
        pass

    def t_BALLOT_END(self, t):
        r"^0[ \t]*\n"
        return t

    # Quoted strings or single words
    def t_STRING(self, t):
        r"\"[^\"]*\"|^[A-Za-z][A-Za-z0-9_\-]*$"
        # Remove quotes if present
        if t.value.startswith('"') and t.value.endswith('"'):
            t.value = t.value[1:-1]
        return t

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
