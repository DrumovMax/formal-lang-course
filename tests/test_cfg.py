import os.path
from project.cfg import cfg_to_wcnf
from project.cfg import get_cfg_from_file


class TestsCFG:
    def test_cfg1(self):
        path = os.path.join("tests", "test_files", "cfg1.txt")
        cfg_wcnf = cfg_to_wcnf(get_cfg_from_file(path))

        compare_path = os.path.join("tests", "test_files", "cfg1_wcnf.txt")
        compare_cfg_wcnf = get_cfg_from_file(compare_path)
        assert cfg_wcnf.productions == compare_cfg_wcnf.productions

    def test_cfg2(self):
        path = os.path.join("tests", "test_files", "cfg2.txt")
        cfg_wcnf = cfg_to_wcnf(get_cfg_from_file(path))

        compare_path = os.path.join("tests", "test_files", "cfg2_wcnf.txt")
        compare_cfg_wcnf = get_cfg_from_file(compare_path)
        assert cfg_wcnf.productions == compare_cfg_wcnf.productions

    def test_cfg3(self):
        path = os.path.join("tests", "test_files", "cfg3.txt")
        cfg_wcnf = cfg_to_wcnf(get_cfg_from_file(path))

        compare_path = os.path.join("tests", "test_files", "cfg3_wcnf.txt")
        compare_cfg_wcnf = get_cfg_from_file(compare_path)
        assert cfg_wcnf.productions == compare_cfg_wcnf.productions
