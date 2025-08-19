from pathlib import Path

import pytest
from lark import UnexpectedInput

from fresh_blt.grammar import blt_parser


def test_invalid_blt_fails_to_parse():
    data_path = Path(__file__).parent / "data" / "invalid.blt"
    data = data_path.read_text()
    with pytest.raises(UnexpectedInput):
        blt_parser.parse(data)
