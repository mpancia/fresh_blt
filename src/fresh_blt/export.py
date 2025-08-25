from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console

from fresh_blt.models.candidate import Candidate

console = Console()


def create_candidates_dataframe(candidates: list[Candidate]) -> pd.DataFrame:
    """Create a pandas DataFrame from candidates data."""
    data = []
    for candidate in candidates:
        data.append({
            "id": candidate.id,
            "name": candidate.name,
            "withdrawn": candidate.withdrawn,
        })

    return pd.DataFrame(data)


def create_ballots_dataframe(ballots: list[dict[str, Any]], candidates: list[Candidate]) -> pd.DataFrame:
    """Create a pandas DataFrame from ballots data."""
    candidate_lookup = {c.id: c.name for c in candidates}

    data = []
    for i, ballot in enumerate(ballots):
        row = {
            "ballot_id": i + 1,
            "weight": ballot["weight"],
        }

        # Add columns for each ranking level
        rankings = ballot["rankings"]
        for rank_idx, rank_candidates in enumerate(rankings):
            if rank_candidates:
                candidate_names = [candidate_lookup[c.id] for c in rank_candidates]
                candidate_ids = [str(c.id) for c in rank_candidates]
                row[f"rank_{rank_idx + 1}_candidates"] = "|".join(candidate_names)
                row[f"rank_{rank_idx + 1}_ids"] = "|".join(candidate_ids)
            else:
                row[f"rank_{rank_idx + 1}_candidates"] = ""
                row[f"rank_{rank_idx + 1}_ids"] = ""

        data.append(row)

    return pd.DataFrame(data)


def create_election_dataframe(election_info: dict[str, Any]) -> pd.DataFrame:
    """Create a pandas DataFrame from election info."""
    return pd.DataFrame([election_info])


def export_to_csv(
    election_info: dict[str, Any],
    candidates: list[Candidate],
    ballots: list[dict[str, Any]],
    output_path: Path
) -> list[Path]:
    """Export election data to multiple CSV files."""
    output_files = []

    # Export election info
    election_file = output_path.with_stem(f"{output_path.stem}_election").with_suffix('.csv')
    election_df = create_election_dataframe(election_info)
    election_df.to_csv(election_file, index=False)
    output_files.append(election_file)
    console.print(f"[green]✓ Exported election info to {election_file}[/green]")

    # Export candidates
    candidates_file = output_path.with_stem(f"{output_path.stem}_candidates").with_suffix('.csv')
    candidates_df = create_candidates_dataframe(candidates)
    candidates_df.to_csv(candidates_file, index=False)
    output_files.append(candidates_file)
    console.print(f"[green]✓ Exported candidates to {candidates_file}[/green]")

    # Export ballots
    ballots_file = output_path.with_stem(f"{output_path.stem}_ballots").with_suffix('.csv')
    ballots_df = create_ballots_dataframe(ballots, candidates)
    ballots_df.to_csv(ballots_file, index=False)
    output_files.append(ballots_file)
    console.print(f"[green]✓ Exported ballots to {ballots_file}[/green]")

    return output_files


def export_to_json(
    election_info: dict[str, Any],
    candidates: list[Candidate],
    ballots: list[dict[str, Any]],
    output_path: Path
) -> Path:
    """Export election data to a comprehensive JSON file."""
    # Prepare data for JSON serialization
    json_candidates = [candidate.model_dump() for candidate in candidates]

    json_ballots = []
    for i, ballot in enumerate(ballots):
        json_ballot = {
            "ballot_id": i + 1,
            "weight": ballot["weight"],
            "rankings": [
                [candidate.model_dump() for candidate in ranking]
                for ranking in ballot["rankings"]
            ]
        }
        json_ballots.append(json_ballot)

    export_data = {
        "election_info": election_info,
        "candidates": json_candidates,
        "ballots": json_ballots,
        "summary": {
            "total_candidates": len(candidates),
            "total_ballots": len(ballots),
            "total_vote_weight": sum(b["weight"] for b in ballots),
            "active_candidates": len([c for c in candidates if not c.withdrawn]),
            "withdrawn_candidates": len([c for c in candidates if c.withdrawn]),
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Exported comprehensive data to {output_path}[/green]")
    return output_path


def export_to_dataframes(
    election_info: dict[str, Any],
    candidates: list[Candidate],
    ballots: list[dict[str, Any]]
) -> dict[str, pd.DataFrame]:
    """Create and return pandas DataFrames for all election data."""
    return {
        "election": create_election_dataframe(election_info),
        "candidates": create_candidates_dataframe(candidates),
        "ballots": create_ballots_dataframe(ballots, candidates),
    }


def export_with_format(
    election_info: dict[str, Any],
    candidates: list[Candidate],
    ballots: list[dict[str, Any]],
    output_path: Path,
    format: str
) -> list[Path] | Path:
    """Export election data in the specified format."""
    if format.lower() == "json":
        return export_to_json(election_info, candidates, ballots, output_path)
    elif format.lower() == "csv":
        return export_to_csv(election_info, candidates, ballots, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")