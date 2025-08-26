"""
Faker provider for generating BLT (Ballot Transmission Language) files.

This module provides a Faker provider that can generate:
- Complete BLT file content
- Election objects with realistic voting patterns
- Individual components (candidates, ballots)
"""

from typing import Any

from faker.providers import BaseProvider

from fresh_blt.models.ballot import Ballot
from fresh_blt.models.candidate import Candidate
from fresh_blt.models.election import Election


class BLTProvider(BaseProvider):
    """
    Faker provider for generating BLT election data.

    Provides methods to generate:
    - Complete BLT file content
    - Election objects with realistic voting patterns
    - Individual components (candidates, ballots)
    """

    def __init__(self, generator):
        super().__init__(generator)
        self._election_counter = 0

    def election_name(self) -> str:
        """Generate a realistic election name."""
        # Election type patterns
        election_types = [
            "Election for {organization}",
            "Steering Committee for {organization}",
            "{group} for {organization}",
            "Board of Directors for {organization}",
            "{group} Election for {organization}",
            "Leadership Committee for {organization}",
            "{group} Council for {organization}",
            "Executive Committee for {organization}",
            "Governing Board for {organization}",
            "{group} Assembly for {organization}",
        ]

        # Group names for elections
        groups = [
            "Management",
            "Executive",
            "Advisory",
            "Oversight",
            "Planning",
            "Finance",
            "Governance",
            "Operations",
            "Strategy",
            "Policy",
            "Technical",
            "Administrative",
            "Coordinating",
            "Review",
            "Selection",
        ]

        # Select random pattern and group
        pattern = self.random_element(election_types)
        group = self.random_element(groups)

        # Generate organization name
        organization = self.generator.company()

        # Format the election name
        return pattern.format(organization=organization, group=group)

    def candidate(self, candidate_id: int, withdrawn_rate: float = 0.1) -> dict[str, Any]:
        """Generate a single candidate."""
        return {
            "id": candidate_id,
            "name": self.generator.name(),
            "withdrawn": self.generator.boolean(chance_of_getting_true=int(withdrawn_rate * 100)),
            "meta": {},
        }

    def ballot(
        self, candidates: list[dict[str, Any]], max_preferences: int | None = None
    ) -> dict[str, Any]:
        """Generate a single ballot with realistic voting patterns."""
        if not candidates:
            return {"rankings": [], "weight": 1}

        # Shuffle candidates to create a random ranking (include all candidates)
        shuffled_candidates = list(candidates)
        self.generator.random.shuffle(shuffled_candidates)

        # Determine how many preferences to include
        if max_preferences is None:
            # Sometimes create partial rankings (70% chance of full ranking, 30% partial)
            if self.generator.boolean(chance_of_getting_true=70):
                num_preferences = len(shuffled_candidates)
            else:
                # Partial ranking: 1 to all-but-one candidates
                num_preferences = self.generator.random_int(
                    min=1, max=max(1, len(shuffled_candidates) - 1)
                )
        else:
            # Respect the max_preferences parameter
            num_preferences = min(max_preferences, len(shuffled_candidates))

        # Create rankings structure with possible ties
        rankings = []
        remaining_candidates = shuffled_candidates[:num_preferences]

        while remaining_candidates:
            # Sometimes create ties (30% chance when there are multiple candidates left)
            if len(remaining_candidates) > 1 and self.generator.boolean(chance_of_getting_true=30):
                # Create a tie: 2-3 candidates at the same preference level
                tie_size = min(self.generator.random_int(min=2, max=3), len(remaining_candidates))
                preference_level = remaining_candidates[:tie_size]
                remaining_candidates = remaining_candidates[tie_size:]
            else:
                # Single candidate at this preference level
                preference_level = [remaining_candidates[0]]
                remaining_candidates = remaining_candidates[1:]

            rankings.append(preference_level)

        # Generate random weight (most ballots have weight 1, some have higher weights)
        if self.generator.boolean(chance_of_getting_true=15):  # 15% chance of weighted ballot
            weight = self.generator.random_int(min=2, max=10)  # Weight between 2-10
        else:
            weight = 1

        return {"rankings": rankings, "weight": weight}

    def election(
        self,
        num_candidates: int | None = None,
        num_ballots: int | None = None,
        withdrawn_rate: float = 0.1,
        num_seats: int = 1,
    ) -> dict[str, Any]:
        """Generate a complete election dataset."""
        if num_candidates is None:
            num_candidates = self.generator.random_int(min=3, max=8)
        if num_ballots is None:
            num_ballots = self.generator.random_int(min=20, max=200)

        # Generate candidates
        candidates = []
        for i in range(num_candidates):
            candidate = self.candidate(candidate_id=i + 1, withdrawn_rate=withdrawn_rate)
            candidates.append(candidate)

        # Generate ballots
        ballots = []
        for _ in range(num_ballots):
            ballot = self.ballot(candidates)
            ballots.append(ballot)

        return {
            "name": self.election_name(),
            "candidates": candidates,
            "ballots": ballots,
            "num_seats": num_seats,
        }

    def close_election(
        self,
        num_candidates: int = 5,
        num_ballots: int = 100,
        withdrawn_rate: float = 0.0,
        num_seats: int = 1,
        closeness_factor: float = 0.8,
    ) -> dict[str, Any]:
        """Generate an election with close results between top candidates."""
        # Generate candidates (no withdrawals for close races)
        candidates = []
        for i in range(num_candidates):
            candidate = self.candidate(candidate_id=i + 1, withdrawn_rate=withdrawn_rate)
            candidates.append(candidate)

        # Target distribution for first preferences to ensure close results
        target_votes = []
        remaining_ballots = num_ballots

        # Generate target vote counts that are close to each other
        for _ in range(num_candidates - 1):
            # Each candidate gets between 15-35% of remaining votes
            min_votes = max(1, int(remaining_ballots * 0.15))
            max_votes = int(remaining_ballots * 0.35)
            votes = self.generator.random_int(min=min_votes, max=max_votes)
            target_votes.append(votes)
            remaining_ballots -= votes

        # Last candidate gets remaining votes
        target_votes.append(remaining_ballots)

        # Shuffle to randomize which candidate gets which vote count
        self.generator.random.shuffle(target_votes)

        # Generate ballots to match target distribution
        ballots = []

        for candidate_idx, target_count in enumerate(target_votes):
            candidate_id = candidate_idx + 1

            for _ in range(target_count):
                # Create ballot favoring this candidate
                ballot = self._generate_close_ballot(candidates, candidate_id, closeness_factor)
                ballots.append(ballot)

        return {
            "name": self.election_name(),
            "candidates": candidates,
            "ballots": ballots,
            "num_seats": num_seats,
        }

    def _generate_close_ballot(
        self,
        candidates: list[dict[str, Any]],
        favored_candidate_id: int,
        closeness_factor: float
    ) -> dict[str, Any]:
        """Generate a ballot that favors a specific candidate but maintains some randomness."""
        # Start with favored candidate first (closeness_factor chance)
        if self.generator.boolean(chance_of_getting_true=int(closeness_factor * 100)):
            # Put favored candidate first
            remaining_candidates = [c for c in candidates if c["id"] != favored_candidate_id]
            self.generator.random.shuffle(remaining_candidates)
            ordered_candidates = [next(c for c in candidates if c["id"] == favored_candidate_id)] + remaining_candidates
        else:
            # Random ordering (for some diversity)
            ordered_candidates = list(candidates)
            self.generator.random.shuffle(ordered_candidates)

        # Create rankings - sometimes full rankings, sometimes partial
        num_preferences = len(ordered_candidates)
        if self.generator.boolean(chance_of_getting_true=20):  # 20% partial rankings
            num_preferences = self.generator.random_int(min=1, max=len(ordered_candidates))

        rankings = []
        for i in range(num_preferences):
            rankings.append([ordered_candidates[i]])

        # Generate weight (mostly 1, occasionally higher)
        weight = 1
        if self.generator.boolean(chance_of_getting_true=10):  # 10% weighted
            weight = self.generator.random_int(min=2, max=5)

        return {"rankings": rankings, "weight": weight}

    def blt_content(self, election_data: dict[str, Any] | None = None) -> str:
        """Generate BLT file content from election data."""
        if election_data is None:
            election_data = self.election()

        lines = []
        candidates = election_data["candidates"]
        ballots = election_data.get("ballots", [])
        num_seats = election_data.get("num_seats", 1)

        # Header: num_candidates num_seats
        num_candidates = len(candidates)
        lines.append(f"{num_candidates} {num_seats}")

        # Withdrawn candidates
        withdrawn_ids = [c["id"] for c in candidates if c["withdrawn"]]
        if withdrawn_ids:
            withdrawn_line = " ".join(f"-{cid}" for cid in sorted(withdrawn_ids))
            lines.append(withdrawn_line)

        # Ballots
        for ballot in ballots:
            ballot_parts = [str(ballot["weight"])]

            for ranking_level in ballot["rankings"]:
                if not ranking_level:  # Empty ranking (exhausted)
                    ballot_parts.append("0")
                else:
                    # Handle ties with = separator
                    candidate_ids = [str(c["id"]) for c in ranking_level]
                    if len(candidate_ids) > 1:
                        ballot_parts.append("=".join(candidate_ids))
                    else:
                        ballot_parts.append(candidate_ids[0])

            ballot_parts.append("0")  # End of ballot
            lines.append(" ".join(ballot_parts))

        # End of ballots marker
        lines.append("0")

        # Candidate names
        for candidate in sorted(candidates, key=lambda c: c["id"]):
            lines.append(f'"{candidate["name"]}"')

        # Election title
        lines.append(f'"{election_data["name"]}"')

        return "\n".join(lines)

    def blt_file(self, filepath: str, election_data: dict[str, Any] | None = None) -> str:
        """Generate and save BLT file."""
        content = self.blt_content(election_data)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return content

    def election_object(self, election_data: dict[str, Any] | None = None):
        """Generate an Election model instance."""
        if election_data is None:
            election_data = self.election()

        # Create Candidate objects from candidate dictionaries
        candidates = []
        for candidate_dict in election_data["candidates"]:
            candidate = Candidate(
                id=candidate_dict["id"],
                name=candidate_dict["name"],
                withdrawn=candidate_dict["withdrawn"],
                meta=candidate_dict.get("meta", {})
            )
            candidates.append(candidate)

        # Create Ballot objects from ballot dictionaries
        ballots = []
        for ballot_dict in election_data["ballots"]:
            # Convert candidate dictionaries back to Candidate objects for rankings
            rankings = []
            for ranking_level in ballot_dict["rankings"]:
                level_candidates = []
                for candidate_dict in ranking_level:
                    # Find the corresponding Candidate object by ID
                    candidate = next(c for c in candidates if c.id == candidate_dict["id"])
                    level_candidates.append(candidate)
                rankings.append(level_candidates)

            ballot = Ballot(
                rankings=rankings,
                weight=ballot_dict["weight"]
            )
            ballots.append(ballot)

        # Create and return Election object
        return Election(
            name=election_data["name"],
            candidates=candidates,
            ballots=ballots
        )
