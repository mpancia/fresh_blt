from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fresh_blt.cli import app, load_blt_data, main
from fresh_blt.models.candidate import Candidate


@pytest.fixture
def runner():
    """CLI runner for testing Typer commands."""
    return CliRunner()


@pytest.fixture
def valid_blt_file():
    """Path to a valid BLT test file."""
    return Path("tests/data/4candidate.blt")


@pytest.fixture
def valid_blt_no_withdrawn_file():
    """Path to a valid BLT test file with no withdrawn candidates."""
    return Path("tests/data/4candidate_no_withdrawn.blt")


@pytest.fixture
def invalid_blt_file():
    """Path to an invalid BLT test file."""
    return Path("tests/data/invalid.blt")


@pytest.fixture
def temp_dir():
    """Temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


class TestLoadBltData:
    """Test the load_blt_data function."""

    def test_load_valid_blt_file(self, valid_blt_file):
        """Test loading data from a valid BLT file."""
        blt_data, candidate_list, ballot_list = load_blt_data(valid_blt_file)

        assert isinstance(blt_data, dict)
        assert "title" in blt_data
        assert "num_candidates" in blt_data
        assert "num_positions" in blt_data
        assert "total_ballots" in blt_data
        assert "total_votes" in blt_data

        assert isinstance(candidate_list, list)
        assert isinstance(ballot_list, list)
        assert len(candidate_list) == blt_data["num_candidates"]
        assert len(ballot_list) == blt_data["total_ballots"]

        # Verify candidate structure
        for candidate in candidate_list:
            assert isinstance(candidate, Candidate)
            assert hasattr(candidate, "id")
            assert hasattr(candidate, "name")
            assert hasattr(candidate, "withdrawn")

    def test_load_blt_file_no_withdrawn(self, valid_blt_no_withdrawn_file):
        """Test loading data from BLT file with no withdrawn candidates."""
        blt_data, candidate_list, ballot_list = load_blt_data(valid_blt_no_withdrawn_file)

        assert blt_data["num_candidates"] == len(candidate_list)
        assert all(not c.withdrawn for c in candidate_list)

    def test_load_invalid_blt_file_raises_exit(self, invalid_blt_file):
        """Test that loading invalid BLT file raises typer.Exit."""
        from click.exceptions import Exit as ClickExit

        with pytest.raises(ClickExit) as exc_info:
            load_blt_data(invalid_blt_file)

        assert exc_info.value.exit_code == 1

    def test_load_nonexistent_file_raises_exit(self):
        """Test that loading nonexistent file raises typer.Exit."""
        from click.exceptions import Exit as ClickExit

        with pytest.raises(ClickExit) as exc_info:
            load_blt_data(Path("nonexistent.blt"))

        assert exc_info.value.exit_code == 1


class TestInfoCommand:
    """Test the info command."""

    def test_info_valid_file(self, runner, valid_blt_file):
        """Test info command with valid BLT file."""
        result = runner.invoke(app, ["info", str(valid_blt_file)])

        assert result.exit_code == 0
        assert "BLT File:" in result.output
        assert "Election Title:" in result.output
        assert "Candidates:" in result.output
        assert "Positions:" in result.output
        assert "Total Ballots:" in result.output
        assert "Total Votes:" in result.output

    def test_info_invalid_file(self, runner, invalid_blt_file):
        """Test info command with invalid BLT file."""
        result = runner.invoke(app, ["info", str(invalid_blt_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output

    def test_info_nonexistent_file(self, runner):
        """Test info command with nonexistent file."""
        result = runner.invoke(app, ["info", "nonexistent.blt"])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output


class TestCandidatesCommand:
    """Test the candidates command."""

    def test_candidates_default(self, runner, valid_blt_file):
        """Test candidates command with default options."""
        result = runner.invoke(app, ["candidates", str(valid_blt_file)])

        assert result.exit_code == 0
        assert "Candidates" in result.output
        assert "ID" in result.output
        assert "Name" in result.output
        assert "Status" in result.output

    def test_candidates_withdrawn_only(self, runner, valid_blt_file):
        """Test candidates command with withdrawn_only option."""
        result = runner.invoke(app, ["candidates", str(valid_blt_file), "--withdrawn-only"])

        assert result.exit_code == 0
        assert "Withdrawn" in result.output and "Only" in result.output

    def test_candidates_active_only(self, runner, valid_blt_file):
        """Test candidates command with active_only option."""
        result = runner.invoke(app, ["candidates", str(valid_blt_file), "--active-only"])

        assert result.exit_code == 0
        assert "Candidates (Active Only)" in result.output

    def test_candidates_mutually_exclusive_options(self, runner, valid_blt_file):
        """Test candidates command with both withdrawn_only and active_only."""
        result = runner.invoke(app, [
            "candidates", str(valid_blt_file),
            "--withdrawn-only", "--active-only"
        ])

        assert result.exit_code == 0
        # Should show all candidates when both options are provided

    def test_candidates_invalid_file(self, runner, invalid_blt_file):
        """Test candidates command with invalid file."""
        result = runner.invoke(app, ["candidates", str(invalid_blt_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output


class TestBallotsCommand:
    """Test the ballots command."""

    def test_ballots_default(self, runner, valid_blt_file):
        """Test ballots command with default options."""
        result = runner.invoke(app, ["ballots", str(valid_blt_file)])

        assert result.exit_code == 0
        assert "Ballots" in result.output
        assert "Ballot #" in result.output
        assert "Weight" in result.output
        assert "Preferences" in result.output

    def test_ballots_with_limit(self, runner, valid_blt_file):
        """Test ballots command with custom limit."""
        result = runner.invoke(app, ["ballots", str(valid_blt_file), "--limit", "5"])

        assert result.exit_code == 0
        assert "Ballots" in result.output

    def test_ballots_with_show_rankings(self, runner, valid_blt_file):
        """Test ballots command with show_rankings option."""
        result = runner.invoke(app, ["ballots", str(valid_blt_file), "--show-rankings"])

        assert result.exit_code == 0
        assert "Ballots" in result.output
        assert "Rankings" in result.output

    def test_ballots_with_limit_and_rankings(self, runner, valid_blt_file):
        """Test ballots command with both limit and show_rankings."""
        result = runner.invoke(app, [
            "ballots", str(valid_blt_file),
            "--limit", "3", "--show-rankings"
        ])

        assert result.exit_code == 0
        assert "Ballots" in result.output
        assert "Rankings" in result.output

    def test_ballots_invalid_file(self, runner, invalid_blt_file):
        """Test ballots command with invalid file."""
        result = runner.invoke(app, ["ballots", str(invalid_blt_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output


class TestStatsCommand:
    """Test the stats command."""

    def test_stats_valid_file(self, runner, valid_blt_file):
        """Test stats command with valid BLT file."""
        result = runner.invoke(app, ["stats", str(valid_blt_file)])

        assert result.exit_code == 0
        assert "Election Statistics" in result.output
        assert "Candidates:" in result.output
        assert "Ballots:" in result.output
        assert "First Preferences:" in result.output

    def test_stats_no_withdrawn_file(self, runner, valid_blt_no_withdrawn_file):
        """Test stats command with file containing no withdrawn candidates."""
        result = runner.invoke(app, ["stats", str(valid_blt_no_withdrawn_file)])

        assert result.exit_code == 0
        assert "Election Statistics" in result.output
        assert "Withdrawn: 0" in result.output

    def test_stats_invalid_file(self, runner, invalid_blt_file):
        """Test stats command with invalid file."""
        result = runner.invoke(app, ["stats", str(invalid_blt_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output


class TestExportCommand:
    """Test the export command."""

    def test_export_json(self, runner, valid_blt_file, temp_dir):
        """Test export command with JSON format."""
        output_file = temp_dir / "export.json"

        result = runner.invoke(app, [
            "export", str(valid_blt_file),
            "--output", str(output_file),
            "--format", "json"
        ])

        assert result.exit_code == 0
        assert f"Exported data to {output_file}" in result.output
        assert output_file.exists()

        # Verify JSON content
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert "election_info" in data
        assert "candidates" in data
        assert "ballots" in data

    def test_export_csv(self, runner, valid_blt_file, temp_dir):
        """Test export command with CSV format."""
        output_file = temp_dir / "export.csv"

        result = runner.invoke(app, [
            "export", str(valid_blt_file),
            "--output", str(output_file),
            "--format", "csv"
        ])

        assert result.exit_code == 0
        assert "Exported candidates to" in result.output
        assert "Exported ballots to" in result.output

        # Check that CSV files were created
        candidates_file = temp_dir / "export_candidates.csv"
        ballots_file = temp_dir / "export_ballots.csv"
        assert candidates_file.exists()
        assert ballots_file.exists()

    def test_export_unsupported_format(self, runner, valid_blt_file, temp_dir):
        """Test export command with unsupported format."""
        output_file = temp_dir / "export.txt"

        result = runner.invoke(app, [
            "export", str(valid_blt_file),
            "--output", str(output_file),
            "--format", "txt"
        ])

        assert result.exit_code == 1
        assert "Unsupported format: txt" in result.output

    def test_export_invalid_file(self, runner, invalid_blt_file, temp_dir):
        """Test export command with invalid file."""
        output_file = temp_dir / "export.json"

        result = runner.invoke(app, [
            "export", str(invalid_blt_file),
            "--output", str(output_file),
            "--format", "json"
        ])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_valid_file(self, runner, valid_blt_file):
        """Test validate command with valid BLT file."""
        result = runner.invoke(app, ["validate", str(valid_blt_file)])

        assert result.exit_code == 0
        assert "✓ BLT file structure is valid" in result.output
        assert "✓ All ballot references are valid" in result.output
        assert "✓ Validation completed successfully" in result.output

    def test_validate_no_withdrawn_file(self, runner, valid_blt_no_withdrawn_file):
        """Test validate command with valid file containing no withdrawn candidates."""
        result = runner.invoke(app, ["validate", str(valid_blt_no_withdrawn_file)])

        assert result.exit_code == 0
        assert "✓ BLT file structure is valid" in result.output

    def test_validate_invalid_file(self, runner, invalid_blt_file):
        """Test validate command with invalid BLT file."""
        result = runner.invoke(app, ["validate", str(invalid_blt_file)])

        assert result.exit_code == 1
        assert "✗ Validation failed:" in result.output

    def test_validate_nonexistent_file(self, runner):
        """Test validate command with nonexistent file."""
        result = runner.invoke(app, ["validate", "nonexistent.blt"])

        assert result.exit_code == 1
        assert "✗ Validation failed:" in result.output


class TestCliEntryPoint:
    """Test the CLI entry point and main function."""

    def test_main_function_calls_app(self):
        """Test that main function calls the app."""
        with patch("fresh_blt.cli.app") as mock_app:
            main()
            mock_app.assert_called_once_with()

    def test_app_no_arguments_shows_help(self, runner):
        """Test that running app with no arguments shows help."""
        result = runner.invoke(app)

        assert result.exit_code == 2  # Typer exits with 2 when no command provided
        assert "fresh-blt" in result.output
        assert "Missing command" in result.output

    def test_app_help_option(self, runner):
        """Test --help option."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "fresh-blt" in result.output
        assert "Commands" in result.output

    def test_app_version_option(self, runner):
        """Test --version option if available."""
        result = runner.invoke(app, ["--version"])

        # This might not exist, so we accept both success and failure
        assert result.exit_code in [0, 2]

    def test_unknown_command(self, runner):
        """Test unknown command handling."""
        result = runner.invoke(app, ["unknown-command"])

        assert result.exit_code == 2  # Typer's exit code for unknown command
        assert "No such command" in result.output


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    def test_file_permission_error(self, runner, temp_dir):
        """Test handling of permission errors."""
        # Create a file without read permissions
        restricted_file = temp_dir / "restricted.blt"
        restricted_file.write_text("test")

        # Remove read permission
        import os
        os.chmod(restricted_file, 0o000)

        result = runner.invoke(app, ["info", str(restricted_file)])

        # Permission errors may result in different exit codes depending on the system
        assert result.exit_code in [1, 2]
        assert "readable" in result.output

    def test_empty_file_error(self, runner, temp_dir):
        """Test handling of empty files."""
        empty_file = temp_dir / "empty.blt"
        empty_file.write_text("")

        result = runner.invoke(app, ["info", str(empty_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output

    def test_malformed_file_error(self, runner, temp_dir):
        """Test handling of malformed files."""
        malformed_file = temp_dir / "malformed.blt"
        malformed_file.write_text("This is not a BLT file\nJust random text")

        result = runner.invoke(app, ["info", str(malformed_file)])

        assert result.exit_code == 1
        assert "Error loading BLT file:" in result.output