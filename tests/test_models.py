def test_sample_election_fixture(sample_election):
    # Check election name
    assert sample_election.name == "Sample Election"

    # Check candidates
    assert len(sample_election.candidates) == 4
    names = {c.name for c in sample_election.candidates}
    assert names == {"Alice", "Bob", "Carol", "Dave"}

    # Check ballots
    assert len(sample_election.ballots) == 2

    # Check first ballot rankings and weight
    ballot1 = sample_election.ballots[0]
    assert ballot1.weight == 2
    assert [[c.name for c in rank] for rank in ballot1.rankings] == [
        ["Alice"],
        ["Bob", "Dave"],
        ["Carol"],
    ]

    # Check second ballot rankings and weight
    ballot2 = sample_election.ballots[1]
    assert ballot2.weight == 1
    assert [[c.name for c in rank] for rank in ballot2.rankings] == [
        ["Bob"],
        ["Alice"],
        ["Dave"],
    ]

    # Check that all candidates are properly created with expected attributes
    for candidate in sample_election.candidates:
        assert hasattr(candidate, 'id')
        assert hasattr(candidate, 'name')
        assert hasattr(candidate, 'withdrawn')


def test_candidate_withdrawn_and_election(sample_election):
    # Carol is withdrawn, others are not
    carol = next(c for c in sample_election.candidates if c.name == "Carol")
    assert carol.withdrawn is True
    # Verify all candidates have required attributes and are not withdrawn (except Carol)
    for c in sample_election.candidates:
        assert hasattr(c, 'id')
        assert hasattr(c, 'name')
        assert hasattr(c, 'withdrawn')
        if c.name != "Carol":
            assert c.withdrawn is False


def test_ballot_rankings_and_weight(sample_election):
    ballot = sample_election.ballots[0]
    # Rankings: Alice > (Bob=Dave) > Carol
    assert ballot.weight == 2
    assert [set(c.name for c in rank) for rank in ballot.rankings] == [
        {"Alice"}, {"Bob", "Dave"}, {"Carol"}
    ]
    # All candidates in ballot rankings are in election.candidates
    all_names = {c.name for c in sample_election.candidates}
    for rank in ballot.rankings:
        for c in rank:
            assert c.name in all_names


def test_election_ballots_and_candidates(sample_election):
    # Ballots should have proper structure and weight
    for ballot in sample_election.ballots:
        assert hasattr(ballot, 'rankings')
        assert hasattr(ballot, 'weight')
        assert ballot.weight > 0
        assert isinstance(ballot.rankings, list)
    # Candidates are unique by id
    ids = [c.id for c in sample_election.candidates]
    assert len(ids) == len(set(ids))