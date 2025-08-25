"""
Tests for the export module.

This module contains comprehensive tests for the export functionality,
including CSV export, JSON export, DataFrame creation, and CLI export commands.
"""

import json
import tempfile
from pathlib import Path

import pytest

from fresh_blt.export import (
    create_ballots_dataframe,
    create_candidates_dataframe,
    create_election_dataframe,
    export_to_csv,
    export_to_dataframes,
    export_to_json,
    export_with_format,
)
from fresh_blt.models.candidate import Candidate


class TestDataFrameCreation:
    """Test cases for DataFrame creation functions."""

    def test_create_candidates_dataframe(self, sample_election):
        """Test creation of candidates DataFrame."""
        df = create_candidates_dataframe(sample_election.candidates)

        assert len(df) == 4
        assert list(df.columns) == ["id", "name", "withdrawn"]
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[2]["withdrawn"] == True  # Carol is withdrawn

    def test_create_election_dataframe(self, sample_election):
        """Test creation of election DataFrame."""
        # Create mock election data
        election_data = {
            "title": "Sample Election",
            "num_candidates": 4,
            "num_positions": 2,
            "withdrawn_candidate_ids": [3],
            "total_ballots": 2,
            "total_votes": 3,
        }

        df = create_election_dataframe(election_data)

        assert len(df) == 1
        assert df.iloc[0]["title"] == "Sample Election"
        assert df.iloc[0]["total_ballots"] == 2

    def test_create_ballots_dataframe(self, sample_election):
        """Test creation of ballots DataFrame."""
        df = create_ballots_dataframe(
            [
                {"weight": 2, "rankings": [sample_election.candidates[:2]]},
                {"weight": 1, "rankings": [sample_election.candidates[2:]]},
            ],
            sample_election.candidates,
        )

        assert len(df) == 2
        assert df.iloc[0]["weight"] == 2
        assert df.iloc[0]["ballot_id"] == 1
        assert "rank_1_candidates" in df.columns
        assert "rank_1_ids" in df.columns


class TestCSVExport:
    """Test cases for CSV export functionality."""

    def test_export_to_csv_creates_files(self, sample_election):
        """Test that CSV export creates the expected files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            # Create mock election data
            election_data = {
                "title": "Test Election",
                "num_candidates": 4,
                "num_positions": 2,
                "withdrawn_candidate_ids": [3],
                "total_ballots": 2,
                "total_votes": 3,
            }

            # Create mock ballot data
            ballots = [
                {"weight": 2, "rankings": [sample_election.candidates[:2]]},
                {"weight": 1, "rankings": [sample_election.candidates[2:]]},
            ]

            files = export_to_csv(election_data, sample_election.candidates, ballots, output_path)

            assert len(files) == 3

            # Check file names and extensions
            file_names = [f.name for f in files]
            assert "test_export_election.csv" in file_names
            assert "test_export_candidates.csv" in file_names
            assert "test_export_ballots.csv" in file_names

            # Verify files exist and have content
            for file_path in files:
                assert file_path.exists()
                content = file_path.read_text()
                assert len(content) > 0

    def test_export_to_csv_file_content(self, sample_election):
        """Test that CSV files contain expected content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            election_data = {
                "title": "Test Election",
                "num_candidates": 4,
                "num_positions": 2,
                "withdrawn_candidate_ids": [3],
                "total_ballots": 2,
                "total_votes": 3,
            }

            ballots = [
                {"weight": 2, "rankings": [sample_election.candidates[:2]]},
            ]

            files = export_to_csv(election_data, sample_election.candidates, ballots, output_path)

            # Check candidates CSV content
            candidates_file = next(f for f in files if "candidates" in f.name)
            content = candidates_file.read_text()
            assert "Alice" in content
            assert "Carol" in content

            # Check election CSV content
            election_file = next(f for f in files if "election" in f.name)
            content = election_file.read_text()
            assert "Test Election" in content


class TestJSONExport:
    """Test cases for JSON export functionality."""

    def test_export_to_json_structure(self, sample_election):
        """Test that JSON export creates expected structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            election_data = {
                "title": "Test Election",
                "num_candidates": 4,
                "num_positions": 2,
                "withdrawn_candidate_ids": [3],
                "total_ballots": 2,
                "total_votes": 3,
            }

            ballots = [
                {"weight": 2, "rankings": [sample_election.candidates[:2]]},
            ]

            result_path = export_to_json(election_data, sample_election.candidates, ballots, output_path)

            assert result_path == output_path
            assert output_path.exists()

            # Parse and verify JSON structure
            with open(output_path) as f:
                data = json.load(f)

            assert "election_info" in data
            assert "candidates" in data
            assert "ballots" in data
            assert "summary" in data

            assert data["election_info"]["title"] == "Test Election"
            assert len(data["candidates"]) == 4
            assert len(data["ballots"]) == 1
            assert data["summary"]["total_candidates"] == 4

    def test_export_to_json_ballot_structure(self, sample_election):
        """Test that JSON ballot data has correct structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            election_data = {"title": "Test Election", "num_candidates": 2, "num_positions": 1,
                           "withdrawn_candidate_ids": [], "total_ballots": 1, "total_votes": 2}

            ballots = [
                {"weight": 2, "rankings": [sample_election.candidates[:2]]},
            ]

            export_to_json(election_data, sample_election.candidates, ballots, output_path)

            with open(output_path) as f:
                data = json.load(f)

            ballot = data["ballots"][0]
            assert ballot["ballot_id"] == 1
            assert ballot["weight"] == 2
            assert "rankings" in ballot


class TestDataFramesExport:
    """Test cases for DataFrames export functionality."""

    def test_export_to_dataframes_returns_all_frames(self, sample_election):
        """Test that export_to_dataframes returns all three DataFrames."""
        election_data = {
            "title": "Test Election",
            "num_candidates": 4,
            "num_positions": 2,
            "withdrawn_candidate_ids": [3],
            "total_ballots": 2,
            "total_votes": 3,
        }

        ballots = [
            {"weight": 2, "rankings": [sample_election.candidates[:2]]},
        ]

        dataframes = export_to_dataframes(election_data, sample_election.candidates, ballots)

        assert "election" in dataframes
        assert "candidates" in dataframes
        assert "ballots" in dataframes

        assert len(dataframes["candidates"]) == 4
        assert len(dataframes["ballots"]) == 1
        assert dataframes["election"].iloc[0]["title"] == "Test Election"


class TestExportWithFormat:
    """Test cases for the unified export_with_format function."""

    def test_export_with_format_csv(self, sample_election):
        """Test export_with_format with CSV format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            election_data = {"title": "Test Election", "num_candidates": 4, "num_positions": 2,
                           "withdrawn_candidate_ids": [], "total_ballots": 1, "total_votes": 2}

            ballots = [{"weight": 1, "rankings": [sample_election.candidates[:2]]}]

            result = export_with_format(election_data, sample_election.candidates, ballots, output_path, "csv")

            assert isinstance(result, list)
            assert len(result) == 3
            assert all(f.exists() for f in result)

    def test_export_with_format_json(self, sample_election):
        """Test export_with_format with JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            election_data = {"title": "Test Election", "num_candidates": 4, "num_positions": 2,
                           "withdrawn_candidate_ids": [], "total_ballots": 1, "total_votes": 2}

            ballots = [{"weight": 1, "rankings": [sample_election.candidates[:2]]}]

            result = export_with_format(election_data, sample_election.candidates, ballots, output_path, "json")

            assert isinstance(result, Path)
            assert result.exists()

            # Verify JSON content
            with open(result) as f:
                data = json.load(f)
                assert data["election_info"]["title"] == "Test Election"

    def test_export_with_format_invalid_format(self, sample_election):
        """Test export_with_format with invalid format raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            election_data = {"title": "Test Election", "num_candidates": 4, "num_positions": 2,
                           "withdrawn_candidate_ids": [], "total_ballots": 1, "total_votes": 2}

            ballots = [{"weight": 1, "rankings": [sample_election.candidates[:2]]}]

            with pytest.raises(ValueError, match="Unsupported format"):
                export_with_format(election_data, sample_election.candidates, ballots, output_path, "xml")