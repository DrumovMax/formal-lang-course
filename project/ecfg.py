from pyformlang.cfg import Variable, Terminal, CFG
from pyformlang.regular_expression import Regex


class ECFG:
    def __init__(
        self,
        variables: set[Variable],
        start_symbol: Variable,
        productions: dict,
        terminals: set[Terminal] = None,
    ):
        self.variables = variables
        self.start_symbol = start_symbol
        self.productions = productions
        self.terminals = terminals

    @classmethod
    def ecfg_from_cfg(cls, cfg: CFG):
        """
        Create ecfg from cfg.

        Parameters
        ----------
        cfg : CFG
            Context-free grammar.
        Returns
        -------
        ecfg : ECFG
            Returns extended context-free grammar.
        """
        productions: dict = {}
        for production in cfg.productions:
            body = Regex(
                " ".join(sym.value for sym in production.body)
                if production.body
                else ""
            )
            productions[production.head] = (
                productions[production.head].union(body)
                if production.head in productions
                else body
            )
        return cls(
            set(cfg.variables), cfg.start_symbol, productions, set(cfg.terminals)
        )

    @classmethod
    def ecfg_from_file(cls, path_to_file):
        """
        Create ecfg from file.

        Parameters:
        ----------
        path_to_file : string
            Path to file.
        Returns:
        --------
        ecfg : ECFG
            Returns extended context-free grammar.
        """
        with open(path_to_file, "r") as file:
            ecfg_string = file.read()
        return cls.ecfg_from_text(ecfg_string)

    @classmethod
    def ecfg_from_text(cls, text: str, start_symbol=Variable("S")):
        """
        Create ecfg from text.

        Parameters:
        ----------
        text : str
            Input string.
        start_symbol : any
            Start non-terminal (variable).
        Returns:
        --------
        ecfg : ECFG
            Returns extended context-free grammar.
        """
        variables = set()
        productions = dict()
        terminals = set()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            [head, body] = line.strip().split("->")
            head = Variable(head.rstrip())
            variables.add(head)
            for sym in body:
                if sym.islower():
                    terminals.add(Terminal(sym))
            productions[head] = body
        return cls(variables, start_symbol, productions, terminals)
