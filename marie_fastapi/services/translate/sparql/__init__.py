from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from .aggregate import GroupByClause
from .graph_pattern import (
    FilterClause,
    GraphPattern,
    TriplePattern,
    ValuesClause,
)
from .query_form import SelectClause
from .sparql_base import SparqlBase


@dataclass(order=True, frozen=True)
class SparqlQuery(SparqlBase):
    select_clause: SelectClause
    graph_patterns: Tuple[GraphPattern, ...]
    groupby_clause: Optional[GroupByClause] = None

    def __init__(
        self, select_clause: SelectClause, graph_patterns: Iterable[GraphPattern], groupby_clause: Optional[GroupByClause] = None
    ):
        object.__setattr__(self, "select_clause", select_clause)
        object.__setattr__(self, "graph_patterns", tuple(graph_patterns))
        object.__setattr__(self, "groupby_clause", groupby_clause)

    def __str__(self):
        return "{select_clause} WHERE {{\n{group_graph_pattern}\n}}{groupby_clause}".format(
            select_clause=self.select_clause,
            group_graph_pattern="\n".join(
                [
                    "  " + line
                    for pattern in self.graph_patterns
                    for line in pattern.tolines()
                ]
            ),
            groupby_clause="\n" + str(self.groupby_clause) if self.groupby_clause is not None else ""
        )

    @classmethod
    def _extract_select_clause(cls, sparql: str):
        """SELECT ?x WHERE {graph_patterns...}"""
        sparql = sparql.strip()
        assert "WHERE" in sparql
        select_clause, sparql = sparql.split("WHERE", maxsplit=1)
        select_clause = select_clause.strip()

        assert select_clause.startswith("SELECT")
        vars = select_clause[len("SELECT") :].strip().split()
        select_clause = SelectClause(vars)

        sparql = sparql.strip()
        assert sparql.startswith("{"), sparql
        assert sparql.endswith("}"), sparql
        graph_patterns_str = sparql[1:-1]

        return select_clause, graph_patterns_str

    @classmethod
    def _extract_values_clause(cls, graph_patterns_str: str):
        """VALUES ?var { {literal} {literal} ... }"""
        graph_patterns_str = graph_patterns_str[len("VALUES") :].strip()
        assert graph_patterns_str.startswith("?"), graph_patterns_str
        var, graph_patterns_str = graph_patterns_str.split(maxsplit=1)
        
        graph_patterns_str = graph_patterns_str.strip()
        assert graph_patterns_str.startswith("{"), graph_patterns_str
        graph_patterns_str = graph_patterns_str[1:].strip()

        ptr = 0
        literals = []
        while ptr < len(graph_patterns_str) and graph_patterns_str[ptr] != "}":
            assert graph_patterns_str[ptr] == '"', graph_patterns_str
            _ptr = ptr + 1
            _ptr_literal_start = _ptr
            while _ptr < len(graph_patterns_str) and graph_patterns_str[_ptr] != '"':
                _ptr += 1
            assert graph_patterns_str[_ptr] == '"'

            literal = graph_patterns_str[_ptr_literal_start:_ptr]
            literals.append(literal)

            ptr = _ptr + 1
            while ptr < len(graph_patterns_str) and graph_patterns_str[ptr].isspace():
                ptr += 1

        values_clause = ValuesClause(var, literals)
        graph_patterns_str = graph_patterns_str[ptr + 1 :]

        return graph_patterns_str, values_clause

    @classmethod
    def _extract_filter_clause(cls, graph_patterns_str: str):
        graph_patterns_str = graph_patterns_str[len("FILTER") :].strip()
        assert graph_patterns_str.startswith("("), graph_patterns_str

        graph_patterns_str = graph_patterns_str[1:].strip()
        ptr = 0
        quote_open = False
        while ptr < len(graph_patterns_str) and (
            graph_patterns_str[ptr] != ")" or quote_open
        ):
            if graph_patterns_str[ptr] == '"':
                quote_open = not quote_open
            ptr += 1
        assert graph_patterns_str[ptr] == ")", graph_patterns_str

        constraint = graph_patterns_str[:ptr].strip()
        filter_clause = FilterClause(constraint)

        graph_patterns_str = graph_patterns_str[ptr + 1 :]

        return graph_patterns_str, filter_clause

    @classmethod
    def _extract_triple_pattern(cls, graph_patterns_str: str):
        subj, graph_patterns_str = graph_patterns_str.split(maxsplit=1)

        tails = []
        while True:
            graph_patterns_str = graph_patterns_str.strip()
            predicate, graph_patterns_str = graph_patterns_str.split(maxsplit=1)

            graph_patterns_str = graph_patterns_str.strip()
            if graph_patterns_str.startswith('"'):
                ptr = 1
                while ptr < len(graph_patterns_str) and graph_patterns_str[ptr] != '"':
                    ptr += 1
                obj = graph_patterns_str[: ptr + 1]
                graph_patterns_str = graph_patterns_str[ptr + 1 :].strip()
            else:
                splits = graph_patterns_str.split(maxsplit=1)
                if len(splits) == 2:
                    obj, graph_patterns_str = splits
                else:
                    (obj,) = splits
                    graph_patterns_str = ""

                if obj.endswith(".") or obj.endswith(";"):
                    punctuation = obj[-1]
                    graph_patterns_str = punctuation + graph_patterns_str
                    obj = obj[:-1]

            tails.append((predicate, obj))

            assert graph_patterns_str[0] in [";", "."], graph_patterns_str
            punctuation = graph_patterns_str[0]
            graph_patterns_str = graph_patterns_str[1:]
            if punctuation == ".":
                break

        triple_pattern = TriplePattern(subj=subj, tails=tails)

        return graph_patterns_str, triple_pattern

    @classmethod
    def fromstring(cls, sparql: str):
        """Parses a SPARQL string to a `SparqlQuery` object."""
        select_clause, graph_patterns_str = cls._extract_select_clause(sparql)

        graph_patterns = []
        while len(graph_patterns_str) > 0:
            graph_patterns_str = graph_patterns_str.strip()
            if graph_patterns_str.startswith("VALUES"):
                graph_patterns_str, pattern = cls._extract_values_clause(
                    graph_patterns_str
                )
            elif graph_patterns_str.startswith("FILTER"):
                graph_patterns_str, pattern = cls._extract_filter_clause(
                    graph_patterns_str
                )
            else:
                graph_patterns_str, pattern = cls._extract_triple_pattern(
                    graph_patterns_str
                )
            graph_patterns.append(pattern)

        return cls(select_clause, graph_patterns)
