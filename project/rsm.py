from pyformlang.cfg import Variable
from project.ecfg import ECFG


class RSM:
    def __init__(self, start_symbol: Variable, boxes: dict):
        self.start_symbol = start_symbol
        self.boxes = boxes

    @classmethod
    def ecfg_to_rsm(cls, ecfg: ECFG):
        """
        Create rsm from ecfg.

        Parameters:
        ----------
        ecfg : ECFG
            Extended Context-Free Grammars.
        Returns:
        -------
        rsm : RSM
            Returns rsm obtained from ecfg.
        """
        boxes = dict()
        for key, value in ecfg.productions.items():
            boxes[key] = value.to_epsilon_nfa()
        return cls(ecfg.start_symbol, boxes)

    def minimize(self):
        """
        Minimize finite automates of rsm.

        Returns:
        ---------
        rsm : Rsm
            Returns minimized rsm.
        """
        for key, value in self.boxes.items():
            self.boxes[key] = value.minimize()
        return self
