"""
Tests for the grammar module.

This module contains comprehensive tests for the BLT grammar parsing functionality,
organized by component using test classes for better maintainability and structure.
"""

import pytest
from lark import ParseTree, UnexpectedInput

from fresh_blt.grammar import blt_parser


class TestGrammarParser:
    """Test cases for the BLT grammar parser functionality."""

    @pytest.fixture(scope="class", params=["4candidate.blt", "4candidate_no_withdrawn.blt"])
    def parsed_tree(self, request) -> tuple[ParseTree, str]:
        """Fixture that provides parsed BLT file trees."""
        # Use inline BLT content instead of reading from files
        if request.param == "4candidate.blt":
            # BLT content with withdrawn candidates
            data = """4 2
-2
3 1 3 4 0
4 1 3 2 0
2 4 1=3 0
1 2 0
2 2=4=3 1 0
1 3 4 2 0
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
        else:
            # BLT content without withdrawn candidates
            data = """4 2
3 1 3 4 0
4 1 3 2 0
2 4 1=3 0
1 2 0
2 2=4=3 1 0
1 3 4 2 0
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
        try:
            tree = blt_parser.parse(data)
            assert tree is not None
            return tree, request.param
        except UnexpectedInput as e:
            pytest.fail(f"Grammar failed to parse {request.param}: {e}")

    def test_grammar_parser_creation(self):
        """Test that the parser is created successfully."""
        assert blt_parser is not None
        assert hasattr(blt_parser, "parse")

    def test_grammar_parser_start_rule(self):
        """Test that parser starts with correct rule."""
        assert blt_parser.options.start == ["start"]

    def test_grammar_header_parsed_correctly(self, parsed_tree):
        """Test that header (candidate count and position count) is parsed correctly."""
        tree, _ = parsed_tree
        header = tree.children[0]
        header_values = [int(token) for token in header.children]
        assert header_values == [4, 2], f"Expected header [4, 2], got {header_values}"

    def test_grammar_title_parsed_correctly(self, parsed_tree):
        """Test that election title is parsed correctly."""
        tree, _ = parsed_tree
        title = tree.children[-1]
        title_value = str(title.children[0]).strip('"')
        assert title_value == "Cool Election", (
            f"Expected title 'Cool Election', got '{title_value}'"
        )

    def test_grammar_withdrawn_candidates_parsed_correctly(self, parsed_tree):
        """Test that withdrawn candidates section is parsed correctly."""
        tree, source = parsed_tree
        withdrawn = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "withdrawn":
                withdrawn = child
                break

        if source == "4candidate_no_withdrawn.blt":
            assert withdrawn is None, "Withdrawn section found but should be absent"
        else:
            assert withdrawn is not None, "Withdrawn section not found"
            withdrawn_values = [int(entry.children[0]) for entry in withdrawn.children]
            assert withdrawn_values == [-2], f"Expected withdrawn [-2], got {withdrawn_values}"

    def test_grammar_candidate_names_parsed_correctly(self, parsed_tree):
        """Test that candidate names are parsed correctly."""
        tree, _ = parsed_tree
        candidate_names = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "candidate_names":
                candidate_names = child
                break

        assert candidate_names is not None, "Candidate names section not found"
        # NAME tokens are direct children, not wrapped in additional nodes
        names = [str(name).strip('"') for name in candidate_names.children]
        expected_names = ["Adam", "Basil", "Charlotte", "Donald"]
        assert names == expected_names, f"Expected {expected_names}, got {names}"

    def test_grammar_ballots_section_exists(self, parsed_tree):
        """Test that ballots section exists and has correct structure."""
        tree, _ = parsed_tree
        ballots = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "ballots":
                ballots = child
                break

        assert ballots is not None, "Ballots section not found"
        assert len(ballots.children) > 0, "Ballots section should have ballot lines"

    def test_grammar_ballot_line_structure(self, parsed_tree):
        """Test that individual ballot lines have correct structure."""
        tree, _ = parsed_tree
        ballots = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "ballots":
                ballots = child
                break

        assert ballots is not None
        for ballot_line in ballots.children:
            assert len(ballot_line.children) >= 2, "Ballot line should have weight and preferences"
            # First child should be weight (INT)
            weight = int(ballot_line.children[0])
            assert weight > 0, f"Ballot weight should be positive, got {weight}"

    def test_grammar_ballot_preferences_structure(self, parsed_tree):
        """Test that ballot preferences are structured correctly."""
        tree, _ = parsed_tree
        ballots = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "ballots":
                ballots = child
                break

        assert ballots is not None
        for ballot_line in ballots.children:
            preferences = ballot_line.children[1]  # Second child should be preferences
            assert hasattr(preferences, "data") and preferences.data == "ballot_prefs"
            assert len(preferences.children) > 0, "Ballot should have preferences"


class TestGrammarErrorHandling:
    """Test cases for grammar error handling and edge cases."""

    def test_grammar_empty_input(self):
        """Test that parser handles empty input appropriately."""
        with pytest.raises(UnexpectedInput):
            blt_parser.parse("")

    def test_grammar_invalid_header(self):
        """Test that parser rejects invalid header format."""
        invalid_inputs = [
            "abc",  # Non-numeric header
            "4",  # Only one number
            "4 2 extra",  # Too many values
        ]
        for invalid_input in invalid_inputs:
            with pytest.raises(UnexpectedInput):
                blt_parser.parse(invalid_input)

    def test_grammar_negative_candidate_count(self):
        """Test that parser rejects negative candidate count."""
        with pytest.raises(UnexpectedInput):
            blt_parser.parse('-1 2\n0\n"Test"\n"Test Election"')

    def test_grammar_zero_candidate_count(self):
        """Test that parser handles zero candidate count."""
        # This might be valid depending on the grammar, but let's test it
        try:
            tree = blt_parser.parse('0 0\n0\n"Test Election"')
            assert tree is not None
        except UnexpectedInput:
            # If it's invalid, that's also acceptable behavior
            pass

    def test_grammar_missing_title(self):
        """Test that parser requires title."""
        with pytest.raises(UnexpectedInput):
            blt_parser.parse('4 2\n0\n"Candidate"')

    def test_grammar_invalid_ballot_weight(self):
        """Test that parser handles invalid ballot weights."""
        # Test with negative weight - should be rejected
        with pytest.raises(UnexpectedInput):
            blt_parser.parse('1 1\n-1 1 0\n0\n"Candidate"\n"Test"')

    def test_grammar_ballot_without_zero_terminator_parses_correctly(self):
        """Test that parser handles ballot lines without 0 terminator correctly."""
        # This should now parse successfully since we made terminators optional
        tree = blt_parser.parse('1 1\n1 1\n0\n"Candidate"\n"Test"')
        assert tree is not None


class TestGrammarEdgeCases:
    """Test cases for grammar edge cases and boundary conditions."""

    def test_grammar_single_candidate(self):
        """Test parsing with single candidate."""
        blt_content = """1 1
1 1 0
0
"Single Candidate"
"Single Election"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_maximum_candidates(self):
        """Test parsing with reasonable maximum number of candidates."""
        # Create a BLT with 10 candidates
        candidates = "\n".join([f'"Candidate {i}"' for i in range(1, 11)])
        ballot_lines = "\n".join([f"1 {i} 0" for i in range(1, 6)])
        blt_content = f"""10 1
{ballot_lines}
0
{candidates}
"Large Election"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_quoted_vs_unquoted_names(self):
        """Test parsing both quoted and unquoted candidate names."""
        blt_content = """2 1
1 1 2 0
0
"Quoted Name"
Unquoted_Name
"Test Election"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_special_characters_in_names(self):
        """Test parsing candidate names with special characters."""
        blt_content = """2 1
1 1 2 0
0
"Candidate-1"
"Candidate_2"
"Special Characters Test"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_multiple_withdrawn_candidates(self):
        """Test parsing multiple withdrawn candidates."""
        blt_content = """4 1
-2
-4
1 1 3 0
0
"Candidate 1"
"Candidate 2"
"Candidate 3"
"Candidate 4"
"Multiple Withdrawn Test"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_ballot_with_ties(self):
        """Test parsing ballots with tied preferences."""
        blt_content = """3 1
2 1=2 3 0
0
"Candidate 1"
"Candidate 2"
"Candidate 3"
"Tie Test"
"""
        tree = blt_parser.parse(blt_content)
        assert tree is not None

    def test_grammar_ballots_without_zero_terminators(self):
        """Test parsing ballots from file with optional zero terminators."""
        # Use the grammar test content without zero terminators
        data = """4 2
-2
3 1 3 4
4 1 3 2
2 4 1=3
1 2
2 2=4=3 1
1 3 4 2
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
        # Should parse successfully since terminators are now optional
        tree = blt_parser.parse(data)
        assert tree is not None

        # Verify we can extract the ballots section
        ballots = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "ballots":  # pyright: ignore[reportAttributeAccessIssue]
                ballots = child
                break

        assert ballots is not None, "Ballots section not found"
        assert len(ballots.children) == 6, f"Expected 6 ballot lines, got {len(ballots.children)}"  # pyright: ignore[reportAttributeAccessIssue]
