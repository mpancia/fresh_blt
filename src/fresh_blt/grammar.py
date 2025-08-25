from lark import Lark

blt_grammar = r"""
start: header _NL withdrawn? ballots "0" _NL candidate_names title _NL?

header: INT INT

withdrawn: (withdrawn_entry _NL)+
withdrawn_entry: SIGNED_INT

ballots: ballot_line+
ballot_line: INT ballot_prefs "0"? _NL
ballot_prefs: ballot_pref+
ballot_pref: INT ("=" INT)*

candidate_names: (NAME _NL)+
title: NAME

NAME: ESCAPED_STRING | WORD

WORD: /[^\s"']+/

_NL: NEWLINE

%import common.INT
%import common.SIGNED_INT
%import common.ESCAPED_STRING
%import common.WS_INLINE
%import common.NEWLINE
%ignore WS_INLINE
"""

blt_parser = Lark(blt_grammar, start="start")
