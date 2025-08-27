from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fresh_blt.export import export_with_format
from fresh_blt.models.candidate import Candidate
from fresh_blt.parse import (
    extract_candidates,
    extract_header_info,
    extract_title,
    parse_ballots,
    parse_blt_file,
)

console = Console()
app = typer.Typer(
    name="fresh-blt",
    help="A CLI tool for parsing and analyzing Opavote .blt files",
    add_completion=False,
)

__all__ = ["main"]

# Module-level variables for Typer defaults to avoid B008 issues
BLT_FILE_ARG = typer.Argument(..., help="Path to the .blt file")
WITHDRAWN_ONLY_OPTION = typer.Option(False, help="Show only withdrawn candidates")
ACTIVE_ONLY_OPTION = typer.Option(False, help="Show only active candidates")
LIMIT_OPTION = typer.Option(10, help="Maximum number of ballots to display")
SHOW_RANKINGS_OPTION = typer.Option(False, help="Show detailed rankings for each ballot")
OUTPUT_OPTION = typer.Option(..., "-o", "--output", help="Output file path")
FORMAT_OPTION = typer.Option("json", "-f", "--format", help="Export format (json, csv)")


def load_blt_data(file_path: Path) -> tuple[dict[str, Any], list[Candidate], list[dict[str, Any]]]:
    """Load and parse .blt file data."""
    try:
        blt_tree = parse_blt_file(file_path)

        # Extract basic information
        num_candidates, num_positions, withdrawn_candidate_ids = extract_header_info(blt_tree)
        title = extract_title(blt_tree)

        # Extract candidates
        candidate_list = extract_candidates(blt_tree, withdrawn_candidate_ids)
        candidate_lookup = {candidate.id: candidate for candidate in candidate_list}

        # Parse ballots
        ballot_list = parse_ballots(blt_tree, candidate_lookup)

        blt_data = {
            "title": title,
            "num_candidates": num_candidates,
            "num_positions": num_positions,
            "withdrawn_candidate_ids": withdrawn_candidate_ids,
            "total_ballots": len(ballot_list),
            "total_votes": sum(ballot["weight"] for ballot in ballot_list),
        }

        return blt_data, candidate_list, ballot_list

    except Exception as e:
        console.print(f"[red]Error loading .blt file: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def info(
    file_path: Path = BLT_FILE_ARG,
) -> None:
    """Display basic information about a .blt file."""
    blt_data, candidate_list, _ = load_blt_data(file_path)

    # Create info panel
    info_text = f"""
[bold]Election Title:[/bold] {blt_data["title"]}
[bold]Candidates:[/bold] {blt_data["num_candidates"]} ({len([c for c in candidate_list if c.withdrawn])} withdrawn)
[bold]Positions:[/bold] {blt_data["num_positions"]}
[bold]Total Ballots:[/bold] {blt_data["total_ballots"]}
[bold]Total Votes:[/bold] {blt_data["total_votes"]}
"""

    panel = Panel(
        info_text.strip(),
        title=f"[bold blue].blt File: {file_path.name}[/bold blue]",
        border_style="blue",
    )
    console.print(panel)


@app.command()
def candidates(
    file_path: Path = BLT_FILE_ARG,
    withdrawn_only: bool = WITHDRAWN_ONLY_OPTION,
    active_only: bool = ACTIVE_ONLY_OPTION,
) -> None:
    """Display candidate information."""
    blt_data, candidate_list, ballot_list = load_blt_data(file_path)

    # Filter candidates based on options
    if withdrawn_only:
        candidates_to_show = [c for c in candidate_list if c.withdrawn]
        title_suffix = " (Withdrawn Only)"
    elif active_only:
        candidates_to_show = [c for c in candidate_list if not c.withdrawn]
        title_suffix = " (Active Only)"
    else:
        candidates_to_show = candidate_list
        title_suffix = ""

    # Create candidates table
    table = Table(title=f"Candidates{title_suffix}")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")

    for candidate in candidates_to_show:
        status = "[red]Withdrawn[/red]" if candidate.withdrawn else "[green]Active[/green]"
        table.add_row(str(candidate.id), candidate.name, status)

    console.print(table)


@app.command()
def ballots(
    file_path: Path = BLT_FILE_ARG,
    limit: int = LIMIT_OPTION,
    show_rankings: bool = SHOW_RANKINGS_OPTION,
) -> None:
    """Display ballot information."""
    blt_data, candidate_list, ballot_list = load_blt_data(file_path)

    candidate_lookup = {c.id: c for c in candidate_list}

    # Create ballots table
    table = Table(title="Ballots")
    table.add_column("Ballot #", style="cyan", no_wrap=True)
    table.add_column("Weight", style="yellow", no_wrap=True)
    if show_rankings:
        table.add_column("Rankings", style="white")
    else:
        table.add_column("Preferences", style="white")

    for i, ballot in enumerate(ballot_list[:limit]):
        weight = ballot["weight"]
        rankings = ballot["rankings"]

        if show_rankings:
            ranking_text = []
            for rank, candidates in enumerate(rankings, 1):
                candidate_names = [candidate_lookup[c.id].name for c in candidates]
                ranking_text.append(f"{rank}: {', '.join(candidate_names)}")
            preferences = "\n".join(ranking_text)
        else:
            # Show first preference only
            first_pref = []
            if rankings and rankings[0]:
                first_pref = [candidate_lookup[c.id].name for c in rankings[0]]
            preferences = ", ".join(first_pref) if first_pref else "No preferences"

        table.add_row(str(i + 1), str(weight), preferences)

    if len(ballot_list) > limit:
        console.print(f"[dim]Showing first {limit} of {len(ballot_list)} ballots[/dim]")

    console.print(table)


@app.command()
def stats(
    file_path: Path = BLT_FILE_ARG,
) -> None:
    """Display statistical analysis of the election."""
    blt_data, candidate_list, ballot_list = load_blt_data(file_path)

    # Calculate statistics
    active_candidates = [c for c in candidate_list if not c.withdrawn]

    # First preference analysis
    first_preferences = {}
    for candidate in active_candidates:
        first_preferences[candidate.id] = 0

    total_weight = 0
    for ballot in ballot_list:
        weight = ballot["weight"]
        total_weight += weight
        rankings = ballot["rankings"]

        if rankings and rankings[0]:
            # Only count preferences for active (non-withdrawn) candidates
            for candidate in rankings[0]:
                if not candidate.withdrawn and candidate.id in first_preferences:
                    first_preferences[candidate.id] += weight

    # Create stats panel
    stats_text = f"""
[bold]Election Statistics[/bold]

[bold]Candidates:[/bold]
  • Total: {len(candidate_list)}
  • Active: {len(active_candidates)}
  • Withdrawn: {len([c for c in candidate_list if c.withdrawn])}

[bold]Ballots:[/bold]
  • Total ballots: {len(ballot_list)}
  • Total vote weight: {total_weight}

[bold]First Preferences:[/bold]
"""

    # Sort candidates by first preference votes
    sorted_candidates = sorted(
        active_candidates, key=lambda c: first_preferences[c.id], reverse=True
    )

    for candidate in sorted_candidates:
        percentage = (
            (first_preferences[candidate.id] / total_weight * 100) if total_weight > 0 else 0
        )
        stats_text += (
            f"  • {candidate.name}: {first_preferences[candidate.id]} votes ({percentage:.1f}%)\n"
        )

    panel = Panel(
        stats_text.strip(),
        title="[bold blue]Election Statistics[/bold blue]",
        border_style="blue",
    )
    console.print(panel)


@app.command()
def export(
    file_path: Path = BLT_FILE_ARG,
    output: Path = OUTPUT_OPTION,
    format: str = FORMAT_OPTION,
) -> None:
    """Export .blt data to JSON or CSV format."""
    blt_data, candidate_list, ballot_list = load_blt_data(file_path)

    try:
        result = export_with_format(blt_data, candidate_list, ballot_list, output, format)

        if format.lower() == "csv" and isinstance(result, list):
            # result is a list of files for CSV format
            console.print(f"[green]✓ Exported data to {len(result)} CSV files[/green]")
        else:
            # result is a single file path for JSON format
            console.print(f"[green]✓ Exported data to {result}[/green]")

    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ Export failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def dataframe(
    file_path: Path = BLT_FILE_ARG,
    show_preview: bool = typer.Option(True, help="Show preview of DataFrames"),
) -> None:
    """Create and display pandas DataFrames from .blt data."""
    try:
        from fresh_blt.export import export_to_dataframes

        blt_data, candidate_list, ballot_list = load_blt_data(file_path)
        dataframes = export_to_dataframes(blt_data, candidate_list, ballot_list)

        console.print("[bold blue]DataFrames Created:[/bold blue]")

        for name, df in dataframes.items():
            console.print(f"\n[bold green]{name.title()} DataFrame:[/bold green]")
            console.print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")

            if show_preview and not df.empty:
                console.print("\n[bold]Preview:[/bold]")
                # Convert to string to avoid rich formatting issues with DataFrames
                preview = str(df.head())
                console.print(preview)

        console.print("\n[dim]DataFrames available as: election, candidates, ballots[/dim]")
        console.print(
            "[dim]Use Python API to access: from fresh_blt.export import export_to_dataframes[/dim]"
        )

    except ImportError:
        console.print("[red]✗ pandas not available.[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗ DataFrame creation failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def validate(
    file_path: Path = BLT_FILE_ARG,
) -> None:
    """Validate the .blt file structure and data."""
    try:
        blt_data, candidate_list, ballot_list = load_blt_data(file_path)

        console.print("[green]✓ .blt file structure is valid[/green]")
        console.print(f"[green]✓ Found {blt_data['num_candidates']} candidates[/green]")
        console.print(f"[green]✓ Found {blt_data['total_ballots']} ballots[/green]")

        # Additional validation checks
        candidate_ids = {c.id for c in candidate_list}
        for ballot in ballot_list:
            for ranking in ballot["rankings"]:
                for candidate in ranking:
                    if candidate.id not in candidate_ids:
                        console.print(f"[red]✗ Invalid candidate ID {candidate.id} in ballot[/red]")
                        raise typer.Exit(1)

        console.print("[green]✓ All ballot references are valid[/green]")
        console.print("[green]✓ Validation completed successfully[/green]")

    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        raise typer.Exit(1) from None


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
