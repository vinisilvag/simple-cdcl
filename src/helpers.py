from dataclasses import dataclass


@dataclass(frozen=True)
class Literal:
    variable: int
    is_negated: bool

    def __repr__(self):
        if self.is_negated:
            return "-" + str(self.variable)
        else:
            return str(self.variable)


@dataclass
class Clause:
    literals: list[Literal]

    def __len__(self):
        return len(self.literals)


@dataclass
class Formula:
    clauses: list[Clause]

    def __len__(self):
        return len(self.clauses)


@dataclass
class Assignment:
    decision_level: int
    literal: int
    value: bool


def print_assignment(assignment: list[Assignment]):
    for lit in assignment:
        print(lit.literal if lit.value else -lit.literal, end=" ")
