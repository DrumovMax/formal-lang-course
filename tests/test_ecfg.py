import pytest
import os.path
from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex
from project.cfg import get_cfg_from_file
from project.fa_utils import create_minimal_dfa
from project.ecfg import ECFG


class TestsCFG:
    ecfg_prods = [
        {
            Variable("S"): Regex("NP VP PUNC"),
            Variable("PUNC"): Regex("\. | !"),
            Variable("VP"): Regex("V NP"),
            Variable("V"): Regex("buys | touches | sees"),
            Variable("NP"): Regex("georges | jacques | leo | Det N"),
            Variable("Det"): Regex("a | an | the"),
            Variable("N"): Regex("gorilla | dog | carrots"),
        },
        {
            Variable("S"): Regex("X Y Z"),
            Variable("X"): Regex("x"),
            Variable("Y"): Regex("y"),
            Variable("Z"): Regex("z"),
        },
        {Variable("S"): Regex("a b c d e")},
    ]
    testdata = [
        (os.path.join("tests", "test_files", "cfg1.txt"), ecfg_prods[0]),
        (os.path.join("tests", "test_files", "cfg2.txt"), ecfg_prods[1]),
        (os.path.join("tests", "test_files", "cfg3.txt"), ecfg_prods[2]),
    ]

    @pytest.mark.parametrize("path_to_file, ecfg_prod", testdata)
    def test_cfg_to_ecfg(self, path_to_file: str, ecfg_prod):
        ecfg = ECFG.ecfg_from_cfg(get_cfg_from_file(path_to_file))
        for key in ecfg_prod.keys():
            minimize_dfa = create_minimal_dfa(ecfg.productions[key])
            compare_minimize_dfa = create_minimal_dfa(ecfg_prod[key])
            if minimize_dfa.is_empty() and compare_minimize_dfa.is_empty():
                continue
            assert minimize_dfa.is_equivalent_to(compare_minimize_dfa)

    @pytest.mark.parametrize("path_to_file, ecfg_prod", testdata)
    def test_ecfg_from_file(self, path_to_file: str, ecfg_prod):
        ecfg = ECFG.ecfg_from_file(path_to_file)
        for key in ecfg_prod.keys():
            minimize_dfa = create_minimal_dfa(Regex(ecfg.productions[key]))
            compare_minimize_dfa = create_minimal_dfa(ecfg_prod[key])
            if minimize_dfa.is_empty() and compare_minimize_dfa.is_empty():
                continue
            assert minimize_dfa.is_equivalent_to(compare_minimize_dfa)

    testdata = [
        (
            """
            S -> NP VP PUNC
            PUNC -> \. | !
            VP -> V NP
            V -> buys | touches | sees
            NP -> georges | jacques | leo | Det N
            Det -> a | an | the
            N -> gorilla | dog | carrots
        """,
            ecfg_prods[0],
        ),
        (
            """
            S -> X Y Z
            X -> x
            Y -> y
            Z -> z
        """,
            ecfg_prods[1],
        ),
        (""" S -> a b c d e """, ecfg_prods[2]),
    ]

    @pytest.mark.parametrize("ecfg_text, ecfg_prod", testdata)
    def test_ecfg_from_text(self, ecfg_text: str, ecfg_prod):
        ecfg = ECFG.ecfg_from_text(ecfg_text)
        for key in ecfg_prod.keys():
            minimize_dfa = create_minimal_dfa(Regex(ecfg.productions[key]))
            compare_minimize_dfa = create_minimal_dfa(ecfg_prod[key])
            if minimize_dfa.is_empty() and compare_minimize_dfa.is_empty():
                continue
            assert minimize_dfa.is_equivalent_to(compare_minimize_dfa)
