from pyformlang.cfg import CFG


def get_cfg_from_file(file) -> CFG:
    """
    Get grammar from file

    Parameters:
    -----------
    file: str
        Path to file.

    Return:
    ----------
    cfg: CFG
        Return CFG.
    """
    with open(file, "r") as file:
        return CFG.from_text(file.read())


def cfg_to_wcnf(cfg: CFG) -> CFG:
    """
    Convert cfg to weak Chomsky normal form(WCNF).

    Parameters:
    -----------
    cfg: CFG
        Context free grammar.

    Return:
    ----------
    cfg_new: CFG
        Context free grammar in WCNF.
    """
    cfg_new = cfg.eliminate_unit_productions().remove_useless_symbols()
    prods = cfg_new._get_productions_with_only_single_terminals()
    return CFG(
        start_symbol=cfg_new.start_symbol,
        productions=set(cfg_new._decompose_productions(prods)),
    )
