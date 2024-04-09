from __future__ import annotations

from typing import Callable, Literal

from rply.errors import ParserGeneratorError
from rply.utils import iteritems


def rightmost_terminal(symbols: list[str], terminals: dict[str, list]):
    for sym in reversed(symbols):
        if sym in terminals:
            return sym
    return None


class Grammar:
    def __init__(self, terminals: list[str]):
        # A list of all the productions
        self.productions: list[Production | None] = [None]
        # A dictionary mapping the names of non-terminals to a list of all
        # productions of that nonterminal
        self.prod_names: dict[str, list] = {}
        # A dictionary mapping the names of terminals to a list of the rules
        # where they are used
        self.terminals: dict[str, list[int]] = dict((t, []) for t in terminals)
        self.terminals["error"] = []
        # A dictionary mapping names of nonterminals to a list of rule numbers
        # where they are used
        self.nonterminals: dict[str, list[int]] = {}
        self.first = {}
        self.follow = {}
        self.precedence: dict[str, tuple[str, int]] = {}
        self.start = None

    def add_production(
        self, prod_name: str, syms: list[str], func: Callable, precedence: str | None
    ):
        if prod_name in self.terminals:
            raise ParserGeneratorError(f"Illegal rule name {prod_name}")

        if precedence is None:
            precname = rightmost_terminal(syms, self.terminals)
            if precname is None:
                prod_prec = ("right", 0)
            else:
                prod_prec = self.precedence.get(precname, ("right", 0))
        else:
            try:
                prod_prec = self.precedence[precedence]
            except KeyError:
                raise ParserGeneratorError(f"Precedence {precedence} doesn't exist")

        pnumber: int = len(self.productions)
        self.nonterminals.setdefault(prod_name, [])

        for t in syms:
            if t in self.terminals:
                self.terminals[t].append(pnumber)
            else:
                self.nonterminals.setdefault(t, []).append(pnumber)

        p = Production(pnumber, prod_name, syms, prod_prec, func)
        self.productions.append(p)

        self.prod_names.setdefault(prod_name, []).append(p)

    def set_precedence(
        self, term: str, assoc: Literal["left", "right", "nonassoc"], level: int
    ):
        if term in self.precedence:
            raise ParserGeneratorError("Precedence already specified for %s" % term)
        if assoc not in ["left", "right", "nonassoc"]:
            raise ParserGeneratorError(
                "Precedence must be one of left, right, nonassoc; not %s" % (assoc)
            )
        self.precedence[term] = (assoc, level)

    def set_start(self):
        if len(self.productions) < 2:
            raise ParserGeneratorError("Grammar must contain at least one rule")
        if self.productions[1] is None:
            raise ParserGeneratorError("Grammar has no start symbol")
        start = self.productions[1].name
        self.productions[0] = Production(0, "S'", [start], ("right", 0), None)
        self.nonterminals[start].append(0)
        self.start = start

    def unused_terminals(self):
        return [
            t for t, prods in iteritems(self.terminals) if not prods and t != "error"
        ]

    def unused_productions(self):
        return [p for p, prods in iteritems(self.nonterminals) if not prods]

    def build_lritems(self):
        """
        Walks the list of productions and builds a complete set of the LR
        items.
        """
        for production in self.productions:
            if production is None:
                continue
            lastlri = production
            i = 0
            lr_items: list[LRItem] = []
            while True:
                if i > len(production):
                    lri = None
                else:
                    try:
                        before = production.prod[i - 1]
                    except IndexError:
                        before = None
                    try:
                        after = self.prod_names[production.prod[i]]
                    except (IndexError, KeyError):
                        after = []
                    lri = LRItem(production, i, before, after)

                lastlri.lr_next = lri

                if lri is None:
                    break
                lr_items.append(lri)
                lastlri = lri
                i += 1
            production.lr_items = lr_items

    def _first(self, beta):
        result = []
        for x in beta:
            x_produces_empty = False
            for f in self.first[x]:
                if f == "<empty>":
                    x_produces_empty = True
                else:
                    if f not in result:
                        result.append(f)
            if not x_produces_empty:
                break
        else:
            result.append("<empty>")
        return result

    def compute_first(self):
        for t in self.terminals:
            self.first[t] = [t]

        self.first["$end"] = ["$end"]

        for n in self.nonterminals:
            self.first[n] = []

        changed = True
        while changed:
            changed = False
            for n in self.nonterminals:
                for p in self.prod_names[n]:
                    for f in self._first(p.prod):
                        if f not in self.first[n]:
                            self.first[n].append(f)
                            changed = True

    def compute_follow(self):
        for k in self.nonterminals:
            self.follow[k] = []

        start = self.start
        self.follow[start] = ["$end"]

        added = True
        while added:
            added = False
            for p in self.productions[1:]:
                for i, B in enumerate(p.prod):
                    if B in self.nonterminals:
                        fst = self._first(p.prod[i + 1 :])
                        has_empty = False
                        for f in fst:
                            if f != "<empty>" and f not in self.follow[B]:
                                self.follow[B].append(f)
                                added = True
                            if f == "<empty>":
                                has_empty = True
                        if has_empty or i == (len(p.prod) - 1):
                            for f in self.follow[p.name]:
                                if f not in self.follow[B]:
                                    self.follow[B].append(f)
                                    added = True


class Production:
    def __init__(
        self,
        num: int,
        name: str,
        prod: list[str],
        precedence: tuple[str, int],
        func: Callable | None,
    ):
        self.name = name
        self.prod = prod
        self.number = num
        self.func = func
        self.prec = precedence
        self.unique_syms = list(set(prod))
        self.lr_items: list[LRItem] = []
        self.lr_next: LRItem | None = None
        self.lr0_added = 0
        self.reduced = 0

    def __repr__(self):
        prods = " ".join(self.prod)
        return f"Production({self.name} -> {prods})"

    def getlength(self):
        return len(self.prod)

    def __len__(self):
        return len(self.prod)

    def set_lr_next(self, lr_next: LRItem | None):
        self.lr_next = lr_next


class LRItem:
    def __init__(self, p: Production, n: int, before, after):
        self.name = p.name
        self.prod = p.prod[:]
        self.prod.insert(n, ".")
        self.number = p.number
        self.lr_index = n
        self.lookaheads = {}
        self.unique_syms = p.unique_syms
        self.lr_before = before
        self.lr_after = after

    def __repr__(self):
        prods = " ".join(self.prod)
        return f"LRItem({self.name} -> {prods})"

    def getlength(self):
        return len(self.prod)

    def __len__(self):
        return len(self.prod)
