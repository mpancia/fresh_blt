from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from lark import Tree

from fresh_blt.models.candidate import Candidate
from fresh_blt.parse import (
    extract_candidates,
    extract_header_info,
    extract_title,
    parse_ballots,
    parse_blt_file,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting BLT file exploration script")

    # Parse BLT file
    blt_path: Path = Path(__file__).parent.parent / "tests" / "data" / "4candidate.blt"
    blt_tree: Tree[Any] = parse_blt_file(blt_path)

    # Extract basic information
    num_candidates, num_positions, withdrawn_candidate_ids = extract_header_info(blt_tree)
    title: str = extract_title(blt_tree)

    # Extract and create candidates
    candidate_list = extract_candidates(blt_tree, withdrawn_candidate_ids)
    candidate_lookup: dict[int, Candidate] = {candidate.id: candidate for candidate in candidate_list}

    # Parse all ballots
    ballot_list: list[dict[str, Any]] = parse_ballots(blt_tree, candidate_lookup)

    logger.info("BLT file processing completed successfully")
    logger.info(f"Summary: {len(candidate_list)} candidates, {len(ballot_list)} ballots, title: '{title}'")

    import code
    code.interact(local=locals())
