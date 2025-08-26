import pytest
from lark import UnexpectedInput

from fresh_blt.grammar import blt_parser


def test_invalid_blt_fails_to_parse():
    """Test that invalid BLT content fails to parse."""
    # Use inline invalid BLT content instead of reading from file
    data = "This is not a valid BLT file\nJust some random text\n123\n"
    with pytest.raises(UnexpectedInput):
        blt_parser.parse(data)
