from pathlib import Path

import pytest
from lark import UnexpectedInput

from fresh_blt.grammar import blt_parser


@pytest.fixture(scope="module")
def parsed_tree():
    data_path = Path(__file__).parent / "data" / "4candidate.blt"
    with open(data_path) as f:
        data = f.read()
    try:
        tree = blt_parser.parse(data)
        assert tree is not None
        return tree
    except UnexpectedInput as e:
        pytest.fail(f"Grammar failed to parse 4candidate.blt: {e}")


def test_grammar_header_parsed_correctly(parsed_tree):
    # The header should be the first child of the tree
    header = parsed_tree.children[0]
    # The header rule should have two INT children: 4 and 2
    header_values = [int(token) for token in header.children]
    assert header_values == [4, 2], f"Expected header [4, 2], got {header_values}"


def test_grammar_title_parsed_correctly(parsed_tree):
    # The title should be the last child of the tree
    title = parsed_tree.children[-1]
    # The title rule should have one child: the string 'Cool Election'
    title_value = str(title.children[0]).strip('"')
    assert title_value == "Cool Election", f"Expected title 'Cool Election', got '{title_value}'"


def test_grammar_withdrawn_candidate_parsed_correctly(parsed_tree):
    # The withdrawn section is the second child if present
    # It should be a subtree with one or more withdrawn_entry children
    # In 4candidate.blt, the withdrawn candidate is -2
    withdrawn = None
    for child in parsed_tree.children:
        if hasattr(child, "data") and child.data == "withdrawn":
            withdrawn = child
            break
    assert withdrawn is not None, "Withdrawn section not found"
    withdrawn_values = [int(entry.children[0]) for entry in withdrawn.children]
    assert withdrawn_values == [-2], f"Expected withdrawn [-2], got {withdrawn_values}"
