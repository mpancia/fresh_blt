# fresh_blt

<div align="center">

```
┌──────────────────────────────────┐
│░█▀▀░█▀▄░█▀▀░█▀▀░█░█░░░█▀▄░█░░░▀█▀│
│░█▀▀░█▀▄░█▀▀░▀▀█░█▀█░░░█▀▄░█░░░░█░│
│░▀░░░▀░▀░▀▀▀░▀▀▀░▀░▀░░░▀▀░░▀▀▀░░▀░│
└──────────────────────────────────┘
```

</div>

A CLI tool and python library for parsing and analyzing Opavote .blt files used in ranked choice voting elections.

## Installation

### From PyPI (Recommended)

Install using your preferred package manager:

**Using uvx (recommended for uv users):**
```bash
uvx fresh_blt --help
```

**Using pipx:**
```bash
pipx install fresh_blt
```

**Using pip:**
```bash
pip install fresh_blt
```

### From Source

For development or to install from the repository:

```bash
uv install .
```

Or using pip:
```bash
pip install .
```

## CLI Usage

The `fresh_blt` CLI provides several commands for working with BLT files:

### Basic Information

Display basic information about a BLT file:

```bash
fresh_blt info path/to/election.blt
```

This shows election title, number of candidates, positions, total ballots, and vote counts.

### Candidate Information

Display candidate information with filtering options:

```bash
# Show all candidates
fresh_blt candidates path/to/election.blt

# Show only withdrawn candidates
fresh_blt candidates path/to/election.blt --withdrawn-only

# Show only active candidates
fresh_blt candidates path/to/election.blt --active-only
```

### Ballot Information

Display ballot information with various options:

```bash
# Show first 10 ballots with first preferences
fresh_blt ballots path/to/election.blt

# Show more ballots
fresh_blt ballots path/to/election.blt --limit 50

# Show detailed rankings for each ballot
fresh_blt ballots path/to/election.blt --show-rankings
```

### Statistical Analysis

Display comprehensive statistical analysis:

```bash
fresh_blt stats path/to/election.blt
```

This provides:
- Candidate counts (total, active, withdrawn)
- Ballot and vote statistics
- First preference analysis with percentages

### Data Export

Export BLT data to JSON or CSV formats with improved structure:

```bash
# Export to JSON (comprehensive format with summary)
fresh_blt export path/to/election.blt -o election_data.json -f json
fresh_blt export path/to/election.blt --output election_data.json --format json

# Export to CSV (creates multiple structured files)
fresh_blt export path/to/election.blt -o election_data.csv -f csv
fresh_blt export path/to/election.blt --output election_data.csv --format csv
# Creates: election_data_election.csv, election_data_candidates.csv, election_data_ballots.csv
```

### DataFrame Creation

Create pandas DataFrames for programmatic analysis:

```bash
# Create DataFrames and show preview
fresh_blt dataframe path/to/election.blt

# Create DataFrames without preview
fresh_blt dataframe path/to/election.blt --no-show-preview
```

### Validation

Validate BLT file structure and data integrity:

```bash
fresh_blt validate path/to/election.blt
```

This checks for:
- Valid file structure
- Correct candidate references in ballots
- Data consistency

## Command Reference

| Command | Description | Options |
|---------|-------------|---------|
| `info` | Display basic election information | None |
| `candidates` | Show candidate details | `--withdrawn-only`, `--active-only` |
| `ballots` | Display ballot information | `--limit`, `--show-rankings` |
| `stats` | Show election statistics | None |
| `export` | Export data to JSON/CSV | `-o/--output`, `-f/--format` |
| `dataframe` | Create pandas DataFrames | `--show-preview/--no-show-preview` |
| `validate` | Validate file structure | None |

## Examples

```bash
# Quick overview of an election
fresh_blt info election.blt

# Analyze candidate performance
fresh_blt stats election.blt

# Extract data for further analysis (using short options)
fresh_blt export election.blt -o analysis.json -f json

# Extract data using long options
fresh_blt export election.blt --output analysis.json --format json

# Check file integrity
fresh_blt validate election.blt
```
