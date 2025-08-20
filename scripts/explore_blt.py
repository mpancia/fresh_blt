from pathlib import Path

from lark import Tree

from fresh_blt.grammar import blt_parser

if __name__ == "__main__":
    blt_path = Path(__file__).parent.parent / "tests" / "data" / "4candidate.blt"
    blt_tree = blt_parser.parse(blt_path.read_text(encoding="utf-8"))
    header: Tree = next(blt_tree.find_data("header"))
    num_candidates = int(header.children[0].value)
    num_positions = int(header.children[1].value)
    if withdrawn := next(blt_tree.find_data("withdrawn"), None):
        withdrawn_candidate_ids = [
            int(entry.children[0].value.strip("-")) for entry in withdrawn.children
        ]
    title = next(blt_tree.find_data("title")).children[0].value.strip('"')
    candidates = [
        (candidate.value.strip('"'), candidate.end_line)
        for candidate in list(blt_tree.find_data("candidate_names"))[0].children
    ]
    ided_candidates = [(x[0], i + 1) for i, x in enumerate(sorted(candidates, key=lambda x: x[1]))]
    ballots = list(blt_tree.find_data("ballots"))
    import code

    code.interact(local=locals())
