from lark import Tree


def parse_tree(blt_tree: 'Tree'):
    header: Tree = next(blt_tree.find_data("header"))
    withdrawn: Tree = next(blt_tree.find_data("withdrawn"), None)
    title = next(blt_tree.find_data("title"))
    ballots = list(blt_tree.find_data("ballots"))
    candidate_names = list(blt_tree.find_data("candidate_names"))