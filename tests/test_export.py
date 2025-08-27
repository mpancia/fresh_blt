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


class TestDataFrameCreation:
    """Test cases for DataFrame creation functions."""

    def test_create_candidates_dataframe(self, sample_election):
        """Test creation of candidates DataFrame."""
        df = create_candidates_dataframe(sample_election.candidates)

        # Check basic structure
        assert len(df) == len(sample_election.candidates)
        assert list(df.columns) == ["id", "name", "withdrawn"]

        # Check that all candidates have valid data
        assert all(isinstance(name, str) and len(name) > 0 for name in df["name"])
        assert all(isinstance(w, bool) for w in df["withdrawn"])

        # Check that IDs are unique and positive
        assert len(df["id"].unique()) == len(df)
        assert all(id > 0 for id in df["id"])

    def test_create_election_dataframe(self, sample_election):
        """Test creation of election DataFrame."""
        # Create election data based on the actual election
        withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
        election_data = {
            "title": sample_election.name,
            "num_candidates": len(sample_election.candidates),
            "num_positions": 1,  # Default for single-winner elections
            "withdrawn_candidate_ids": withdrawn_ids,
            "total_ballots": len(sample_election.ballots),
            "total_votes": sum(b.weight for b in sample_election.ballots),
        }

        df = create_election_dataframe(election_data)

        assert len(df) == 1
        assert df.iloc[0]["title"] == sample_election.name
        assert df.iloc[0]["num_candidates"] == len(sample_election.candidates)
        assert df.iloc[0]["total_ballots"] == len(sample_election.ballots)

    def test_create_ballots_dataframe(self, sample_election):
        """Test creation of ballots DataFrame."""
        # Create test ballot data using actual candidates from the election
        candidates = sample_election.candidates
        if len(candidates) < 2:
            pytest.skip("Need at least 2 candidates for ballot test")

        # Create a couple of test ballots
        test_ballots = [
            {
                "weight": 2,
                "rankings": [[candidates[0]], [candidates[1]]],  # First > Second
            },
            {
                "weight": 1,
                "rankings": [[candidates[1]], [candidates[0]]],  # Second > First
            },
        ]

        df = create_ballots_dataframe(test_ballots, candidates)

        assert len(df) == 2
        assert df.iloc[0]["weight"] == 2
        assert df.iloc[0]["ballot_id"] == 1
        assert "rank_1_candidates" in df.columns
        assert "rank_1_ids" in df.columns

        # Check that candidate names appear in the dataframe
        candidate_names = {c.name for c in candidates}
        content = df.to_string()
        assert any(name in content for name in candidate_names)


class TestCSVExport:
    """Test cases for CSV export functionality."""

    def test_export_to_csv_creates_files(self, sample_election):
        """Test that CSV export creates the expected files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Create ballot data using actual election ballots
            ballots = []
            for _i, ballot in enumerate(sample_election.ballots):
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

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

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            files = export_to_csv(election_data, sample_election.candidates, ballots, output_path)

            # Check candidates CSV content
            candidates_file = next(f for f in files if "candidates" in f.name)
            content = candidates_file.read_text()

            # Verify that candidate names from the election appear in the CSV
            for candidate in sample_election.candidates:
                assert candidate.name in content

            # Check election CSV content
            election_file = next(f for f in files if "election" in f.name)
            content = election_file.read_text()
            assert sample_election.name in content


class TestJSONExport:
    """Test cases for JSON export functionality."""

    def test_export_to_json_structure(self, sample_election):
        """Test that JSON export creates expected structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            result_path = export_to_json(
                election_data, sample_election.candidates, ballots, output_path
            )

            assert result_path == output_path
            assert output_path.exists()

            # Parse and verify JSON structure
            with open(output_path) as f:
                data = json.load(f)

            assert "election_info" in data
            assert "candidates" in data
            assert "ballots" in data
            assert "summary" in data

            assert data["election_info"]["title"] == sample_election.name
            assert len(data["candidates"]) == len(sample_election.candidates)
            assert len(data["ballots"]) == len(sample_election.ballots)
            assert data["summary"]["total_candidates"] == len(sample_election.candidates)

    def test_export_to_json_ballot_structure(self, sample_election):
        """Test that JSON ballot data has correct structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            export_to_json(election_data, sample_election.candidates, ballots, output_path)

            with open(output_path) as f:
                data = json.load(f)

            # Check that we have ballots and they have the expected structure
            assert len(data["ballots"]) > 0
            ballot = data["ballots"][0]
            assert ballot["ballot_id"] == 1
            assert "weight" in ballot
            assert "rankings" in ballot
            assert isinstance(ballot["weight"], int)
            assert ballot["weight"] > 0


class TestDataFramesExport:
    """Test cases for DataFrames export functionality."""

    def test_export_to_dataframes_returns_all_frames(self, sample_election):
        """Test that export_to_dataframes returns all three DataFrames."""
        # Create election data based on the actual election
        withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
        election_data = {
            "title": sample_election.name,
            "num_candidates": len(sample_election.candidates),
            "num_positions": 1,
            "withdrawn_candidate_ids": withdrawn_ids,
            "total_ballots": len(sample_election.ballots),
            "total_votes": sum(b.weight for b in sample_election.ballots),
        }

        # Use actual ballots from the election
        ballots = []
        for ballot in sample_election.ballots:
            ballot_dict = {
                "weight": ballot.weight,
                "rankings": [[c for c in ranking] for ranking in ballot.rankings],
            }
            ballots.append(ballot_dict)

        dataframes = export_to_dataframes(election_data, sample_election.candidates, ballots)

        assert "election" in dataframes
        assert "candidates" in dataframes
        assert "ballots" in dataframes

        assert len(dataframes["candidates"]) == len(sample_election.candidates)
        assert len(dataframes["ballots"]) == len(sample_election.ballots)
        assert dataframes["election"].iloc[0]["title"] == sample_election.name


class TestExportWithFormat:
    """Test cases for the unified export_with_format function."""

    def test_export_with_format_csv(self, sample_election):
        """Test export_with_format with CSV format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            result = export_with_format(
                election_data, sample_election.candidates, ballots, output_path, "csv"
            )

            assert isinstance(result, list)
            assert len(result) == 3
            assert all(f.exists() for f in result)

    def test_export_with_format_json(self, sample_election):
        """Test export_with_format with JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            result = export_with_format(
                election_data, sample_election.candidates, ballots, output_path, "json"
            )

            assert isinstance(result, Path)
            assert result.exists()

            # Verify JSON content
            with open(result) as f:
                data = json.load(f)
                assert data["election_info"]["title"] == sample_election.name

    def test_export_with_format_invalid_format(self, sample_election):
        """Test export_with_format with invalid format raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"

            # Create election data based on the actual election
            withdrawn_ids = [c.id for c in sample_election.candidates if c.withdrawn]
            election_data = {
                "title": sample_election.name,
                "num_candidates": len(sample_election.candidates),
                "num_positions": 1,
                "withdrawn_candidate_ids": withdrawn_ids,
                "total_ballots": len(sample_election.ballots),
                "total_votes": sum(b.weight for b in sample_election.ballots),
            }

            # Use actual ballots from the election
            ballots = []
            for ballot in sample_election.ballots:
                ballot_dict = {
                    "weight": ballot.weight,
                    "rankings": [[c for c in ranking] for ranking in ballot.rankings],
                }
                ballots.append(ballot_dict)

            with pytest.raises(ValueError, match="Unsupported format"):
                export_with_format(
                    election_data, sample_election.candidates, ballots, output_path, "xml"
                )
