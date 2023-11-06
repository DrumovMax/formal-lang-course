import pytest
import os.path
from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex
from project.cfg import get_cfg_from_file
from project.fa_utils import create_minimal_dfa
from project.ecfg import ECFG
from project.rsm import RSM


class TestsRSM:
    testdata = [
        (
            os.path.join("tests", "test_files", "cfg1.txt"),
            {
                Variable("S"): Regex("NP VP PUNC"),
                Variable("PUNC"): Regex("\. | !"),
                Variable("VP"): Regex("V NP"),
                Variable("V"): Regex("buys | touches | sees"),
                Variable("NP"): Regex("georges | jacques | leo | Det N"),
                Variable("Det"): Regex("a | an | the"),
                Variable("N"): Regex("gorilla | dog | carrots"),
            },
        ),
        (
            os.path.join("tests", "test_files", "cfg2.txt"),
            {
                Variable("S"): Regex("X Y Z"),
                Variable("X"): Regex("x"),
                Variable("Y"): Regex("y"),
                Variable("Z"): Regex("z"),
            },
        ),
        (
            os.path.join("tests", "test_files", "cfg3.txt"),
            {Variable("S"): Regex("a b c d e")},
        ),
    ]

    @pytest.mark.parametrize("path_to_file, ecfg_prod", testdata)
    def test_ecfg_rsm(self, path_to_file, ecfg_prod):
        rsm = RSM.ecfg_to_rsm(ECFG.ecfg_from_cfg(get_cfg_from_file(path_to_file)))
        for key in ecfg_prod.keys():
            compare_dfa = create_minimal_dfa(ecfg_prod[key])
            if rsm.boxes[key].is_empty() and compare_dfa.is_empty():
                continue
            assert rsm.boxes[key].is_equivalent_to(compare_dfa)
