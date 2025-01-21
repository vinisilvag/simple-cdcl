from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Literal:
    variable: int
    is_negated: bool

    def __repr__(self):
        if self.is_negated:
            return "-" + str(self.variable)
        else:
            return str(self.variable)

    def negation(self):
        return Literal(self.variable, not self.is_negated)


@dataclass
class Clause:
    literals: list[Literal]

    def __len__(self):
        return len(self.literals)

    def __contains__(self, literal: int):
        literal_aux = Literal(literal, False)
        return (literal_aux in self.literals) or (
            literal_aux.negation() in self.literals
        )


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
    antecedent: Optional[int]

    def __contains__(self, literal: int):
        return literal == self.literal

    def __repr__(self):
        literal = "-" + str(self.literal) if self.value == False else str(self.literal)
        return "({} @ {}, {})".format(
            literal,
            self.decision_level,
            None if not self.antecedent else "c" + str(self.antecedent),
        )


def print_assignment(assignment: list[Assignment]):
    for lit in assignment:
        print(lit.literal if lit.value else -lit.literal, end=" ")
