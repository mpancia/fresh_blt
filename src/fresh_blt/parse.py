from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from lark import Tree

from fresh_blt.grammar import blt_parser
from fresh_blt.models.candidate import Candidate

logger = logging.getLogger(__name__)


def parse_blt_file(blt_path: Path) -> Tree[Any]:
    """
    Parse BLT file into a syntax tree.

    Args:
        blt_path: Path to the BLT file

    Returns:
        Parse tree representing the BLT file structure
    """
    logger.info(f"Parsing BLT file: {blt_path}")
    return blt_parser.parse(blt_path.read_text(encoding="utf-8"))


def extract_header_info(blt_tree: Tree[Any]) -> tuple[int, int, list[int]]:
    """
    Extract header information from the parse tree.

    Args:
        blt_tree: Parse tree of the BLT file

    Returns:
        Tuple of (num_candidates, num_positions, withdrawn_candidate_ids)
    """
    logger.info("Extracting header information")
    header: Tree[Any] = next(blt_tree.find_data("header"))
    num_candidates: int = int(header.children[0].value)  # pyright: ignore
    num_positions: int = int(header.children[1].value)  # pyright: ignore

    withdrawn_candidate_ids = []
    if withdrawn := next(blt_tree.find_data("withdrawn"), None):
        withdrawn_candidate_ids: list[int] = [
            int(entry.children[0].value.strip("-"))  # pyright: ignore
            for entry in withdrawn.children  # pyright: ignore
        ]

    logger.info(f"Found {num_candidates} candidates, {num_positions} positions, {len(withdrawn_candidate_ids)} withdrawn candidates")
    return num_candidates, num_positions, withdrawn_candidate_ids


def extract_title(blt_tree: Tree[Any]) -> str:
    """
    Extract election title from the parse tree.

    Args:
        blt_tree: Parse tree of the BLT file

    Returns:
        Election title as string
    """
    title = next(blt_tree.find_data("title")).children[0].value.strip('"')  # pyright: ignore
    logger.info(f"Extracted election title: {title}")
    return title


def extract_candidates(blt_tree: Tree[Any], withdrawn_candidate_ids: list[int]) -> list[Candidate]:
    """
    Extract and create candidate objects from the parse tree.

    Args:
        blt_tree: Parse tree of the BLT file
        withdrawn_candidate_ids: List of withdrawn candidate IDs

    Returns:
        List of Candidate objects
    """
    logger.info("Extracting candidates from parse tree")
    candidates: list[tuple[str, int]] = [
        (candidate.value.strip('"'), candidate.end_line)  # pyright: ignore
        for candidate in list(blt_tree.find_data("candidate_names"))[0].children  # pyright: ignore
    ]
    ided_candidates: list[tuple[str, int]] = [
        (x[0], i + 1) for i, x in enumerate(sorted(candidates, key=lambda x: x[1]))
    ]

    candidate_list = []
    for (candidate_name, id) in ided_candidates:
        is_withdrawn = id in withdrawn_candidate_ids
        candidate_list.append(
            Candidate.from_dict({
                "id": id,
                "name": candidate_name,
                "withdrawn": is_withdrawn
            })
        )
        logger.debug(f"Created candidate: {candidate_name} (ID: {id}, Withdrawn: {is_withdrawn})")

    logger.info(f"Created {len(candidate_list)} candidates, {len(withdrawn_candidate_ids)} withdrawn")
    return candidate_list


def parse_ballots(blt_tree: Tree[Any], candidate_lookup: dict[int, Candidate]) -> list[dict[str, Any]]:
    """
    Parse all ballots from the parse tree.

    Args:
        blt_tree: Parse tree of the BLT file
        candidate_lookup: Dictionary mapping candidate IDs to Candidate objects

    Returns:
        List of parsed ballot dictionaries

    Raises:
        ValueError: If any ballot has invalid structure
    """
    ballots_trees: list[Tree[Any]] = list(blt_tree.find_data("ballots"))[0].children
    ballot_list: list[dict[str, Any]] = []

    logger.info(f"Parsing {len(ballots_trees)} ballots")
    for ballot_index, ballot_tree in enumerate(ballots_trees):
        try:
            parsed_ballot = parse_ballot(ballot_tree, candidate_lookup)
            ballot_list.append(parsed_ballot)
            logger.debug(f"Successfully parsed ballot {ballot_index + 1}")
        except ValueError as e:
            logger.error(f"Error parsing ballot {ballot_index + 1}: {e}")
            raise ValueError(f"Error parsing ballot {ballot_index + 1}: {e}") from e

    logger.info(f"Successfully parsed all {len(ballot_list)} ballots")
    return ballot_list


def parse_ballot(ballot_tree: Tree[Any], candidate_lookup: dict[int, Candidate]) -> dict[str, Any]:
    """
    Parse a single ballot from the parse tree.

    Args:
        ballot_tree: Parse tree node representing a ballot
        candidate_lookup: Dictionary mapping candidate IDs to Candidate objects

    Returns:
        Dictionary containing ballot weight and rankings

    Raises:
        ValueError: If ballot structure is malformed or contains invalid data
    """
    if len(ballot_tree.children) < 2:
        raise ValueError("Ballot must have at least weight and preferences")

    try:
        weight = int(ballot_tree.children[0].value)  # pyright: ignore[reportAttributeAccessIssue]
        if weight <= 0:
            raise ValueError(f"Ballot weight must be positive, got {weight}")
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid ballot weight: {e}") from e

    rankings: list[list[Candidate]] = []
    preferences_node = ballot_tree.children[1]

    for _, candidates_node in enumerate(preferences_node.children):
        candidates_at_level = parse_ballot_candidates(candidates_node, candidate_lookup)
        if candidates_at_level:  # Only add non-empty preference levels
            rankings.append(candidates_at_level)

    return {
        "weight": weight,
        "rankings": rankings
    }


def parse_ballot_candidates(candidates_node: Tree[Any] | list[Any], candidate_lookup: dict[int, Candidate]) -> list[Candidate]:
    """
    Parse candidate preferences from a ballot preference node.

    Args:
        candidates_node: Either a Tree node or list of candidate nodes
        candidate_lookup: Dictionary mapping candidate IDs to Candidate objects for O(1) lookup

    Returns:
        List of Candidate objects for this preference level

    Raises:
        ValueError: If a candidate ID is not found in the lookup table
    """
    candidates_at_level: list[Candidate] = []

    if isinstance(candidates_node, list):
        # Multiple candidates at this preference level (tied candidates)
        for candidate_node in candidates_node:
            candidate_id = int(candidate_node.value)
            if candidate_id not in candidate_lookup:
                raise ValueError(f"Invalid candidate ID {candidate_id} not found in candidate list")
            candidates_at_level.append(candidate_lookup[candidate_id])
    else:
        # Single candidate at this preference level
        if not candidates_node.children:
            return candidates_at_level  # Empty preference level

        candidate_id = int(candidates_node.children[0].value)  # pyright: ignore[reportAttributeAccessIssue]
        if candidate_id not in candidate_lookup:
            raise ValueError(f"Invalid candidate ID {candidate_id} not found in candidate list")
        candidates_at_level.append(candidate_lookup[candidate_id])

    return candidates_at_level