from pathlib import Path

import pytest

from fresh_blt.lexer import BltLexer


@pytest.fixture
def blt_lexer():
    lexer = BltLexer()
    lexer.build()
    return lexer

def test_lexer_on_4candidate_blt(blt_lexer):
    data_path = Path(__file__).parent / "data" / "4candidate.blt"
    with open(data_path) as f:
        data = f.read()
    blt_lexer.test(data)
    blt_lexer.lexer.input(data)
    tokens = list(blt_lexer.lexer)
    assert tokens[0].type == "NUMBER"
    assert tokens[0].value == 4
    assert tokens[1].type == "NUMBER"
    assert tokens[1].value == 2
    # Check for a STRING token (candidate name)
    string_tokens = [t for t in tokens if t.type == "STRING"]
    assert any(t.value == "Adam" for t in string_tokens)
    assert any(t.value == "Cool Election" for t in string_tokens)
    # Check for a MINUS token (skipped ranking)
    assert any(t.type == "MINUS" for t in tokens)
    # Check for an EQUALS token (overvote)
    assert any(t.type == "EQUALS" for t in tokens)
    # Check for a ZERO token (standalone zero)
    assert any(t.type == "ZERO" for t in tokens)
