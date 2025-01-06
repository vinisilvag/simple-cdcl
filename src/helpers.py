from dataclasses import dataclass


@dataclass
class Literal:
    lit: int
    is_negated: bool


@dataclass
class Clause:
    literals: list[Literal]


@dataclass
class Formula:
    clauses: list[Clause]


@dataclass
class Assignment:
    decision_level: int
    literal: int
    value: bool


def print_assignment(assignment: list[Assignment]):
    for lit in assignment:
        print(lit.literal if lit.value else -lit.literal, end=" ")
