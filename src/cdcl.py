from collections import defaultdict
from typing import Optional

from helpers import Assignment, Formula, Literal


class CDCL:
    def __init__(self, variable_num, clause_num, formula):
        self.variable_num: int = variable_num
        self.clause_num: int = clause_num
        self.formula: Formula = formula

        self.M: list[Assignment] = []
        self.assignment: list[Optional[bool]] = [
            None for _ in range(self.variable_num + 1)
        ]
        self.decision_level = 0
        self.watched_literals: dict[Literal, list[int]] = defaultdict(list)

        # initialize the 2 watched literals data structure
        for clause_index, clause in enumerate(formula.clauses):
            if len(clause) < 2:
                continue
            self.watched_literals[clause.literals[0]].append(clause_index)
            self.watched_literals[clause.literals[1]].append(clause_index)

        # VSIDS
        self.activity: dict[Literal, float] = defaultdict(int)
        self.decay_factor = 0.95
        self.increment = 1

    def apply_decay(self):
        for variable in self.activity:
            self.activity[variable] *= self.decay_factor

    def assign(self, variable: int, value: bool):
        self.M.append(Assignment(self.decision_level, variable, value))
        self.assignment[variable] = value

    def unassign(self, remove: int):
        self.assignment[self.M[remove].literal] = None
        self.M.pop(remove)

    def solve_only_negative_or_positive_literals(self) -> list[Literal]:
        print("\nliterais apenas positivos ou negativos na formula")
        literal_count = defaultdict(int)
        to_propagate = []

        for clause in self.formula.clauses:
            for literal in clause.literals:
                literal_count[literal] += 1
                literal_count[literal.negation()] += 0

        for lit, count in literal_count.items():
            if count > 0 and literal_count[lit.negation()] == 0:
                if self.assignment[lit.variable] == None:
                    self.assign(lit.variable, not lit.is_negated)
                    to_propagate.append(lit)

        print("to unit propagate")
        print(to_propagate)
        return to_propagate

    def solve_unit_clauses(self) -> Optional[list[Literal]]:
        print("\nclausulas com apenas um literal...")
        to_propagate = []

        for _, clause in enumerate(self.formula.clauses):
            if len(clause.literals) == 1:
                literal = clause.literals[0]
                if self.assignment[literal.variable] == None:
                    self.assign(literal.variable, not literal.is_negated)
                    to_propagate.append((literal))
                else:
                    assignment = self.assignment[literal.variable]
                    if (assignment and literal.is_negated) or (
                        not assignment and not literal.is_negated
                    ):
                        # two conflitant unit clauses
                        return None

        print("to unit propagate")
        print(to_propagate)
        return to_propagate

    def all_clauses_are_satisfied(self) -> bool:
        satisfied = 0

        for clause in self.formula.clauses:
            literals = clause.literals
            for literal in literals:
                assignment = self.assignment[literal.variable]
                if assignment == None:
                    continue
                elif (assignment and not literal.is_negated) or (
                    not assignment and literal.is_negated
                ):
                    satisfied += 1

        return satisfied == self.clause_num

    def unit_propagation(
        self, to_propagate: list[Literal]
    ) -> tuple[int, Optional[int]]:
        while len(to_propagate) > 0:
            # if we assign a literal, then we have to update the watched literals
            # for the clauses that are currently watching -literal
            literal = to_propagate.pop()
            negated_lit = literal.negation()
            clauses = list(self.watched_literals[negated_lit])

            for clause in clauses:
                literals = self.formula.clauses[clause].literals

                watched_literal_changed = False
                for lit in literals:
                    if clause in self.watched_literals[lit]:
                        # literal already watched
                        continue

                    # rewatch a non assigned literal
                    if self.assignment[lit.variable] == None:
                        self.watched_literals[negated_lit].remove(clause)
                        self.watched_literals[lit].append(clause)
                        watched_literal_changed = True
                        break
                    else:
                        assignment = self.assignment[lit.variable]
                        if (assignment and lit.is_negated) or (
                            not assignment and not lit.is_negated
                        ):
                            # falsified literal, skip
                            continue
                        else:
                            # rewatch a True literal
                            self.watched_literals[negated_lit].remove(clause)
                            self.watched_literals[lit].append(clause)
                            watched_literal_changed = True
                            break

                if not watched_literal_changed:
                    # cannot find another literal to rewatch
                    literals = [
                        key
                        for key, clauses_watching in self.watched_literals.items()
                        if clause in clauses_watching
                    ]

                    other_watched_literal = (
                        literals[0] if literals[1] == negated_lit else literals[1]
                    )
                    if self.assignment[other_watched_literal.variable] == None:
                        # unit clause, propagate too
                        self.assign(
                            other_watched_literal.variable,
                            not other_watched_literal.is_negated,
                        )
                        to_propagate.append(other_watched_literal)
                    else:
                        assignment = self.assignment[other_watched_literal.variable]
                        if (assignment and not other_watched_literal.is_negated) or (
                            not assignment and other_watched_literal.is_negated
                        ):
                            # True literal, skip clause
                            continue
                        else:
                            # False literal too, conflict
                            return 1, clause

        return 0, None

    def choose_literal(self):
        candidates = []
        for i in range(1, self.variable_num + 1):
            if self.assignment[i] == None:
                literal = Literal(i, False)
                candidates.append(literal)
                candidates.append(literal.negation())

        candidates.sort(key=lambda i: self.activity[i], reverse=True)

        candidate = candidates[0]
        return candidate, not candidate.is_negated

    def conflict_analysis(self, clause: int) -> int:
        new_decision_level = -1

        # update activity for literals in the conflict clause
        for literal in self.formula.clauses[clause].literals:
            self.activity[literal] += self.increment

        # handle conflict analysis

        # apply decay
        self.apply_decay()

        return new_decision_level

    def solve(self):
        # purify step
        to_propagate = []
        to_propagate.extend(self.solve_only_negative_or_positive_literals())
        literals_from_unit_clauses = self.solve_unit_clauses()

        # two conflitant unit clauses
        if literals_from_unit_clauses == None:
            return None

        to_propagate.extend(literals_from_unit_clauses)

        print("\nafter purify")
        print(self.M)

        print("\n-------------------------------------------------")

        print("\npropagating after purify")
        print("to unit propagate")
        print(to_propagate)

        status, _ = self.unit_propagation(to_propagate)
        # conflict, formula is UNSAT
        if status == 1:
            return None

        print("\nafter propagating")
        print(self.M)

        print("\n-------------------------------------------------")

        print("\nstarting propagation and deciding or end")
        while not self.all_clauses_are_satisfied():
            literal, value = self.choose_literal()
            print("\ndeciding:", literal.variable, "vale", value)
            self.decision_level += 1
            self.assign(literal.variable, value)
            to_propagate.append(literal)

            while True:
                print("\nto unit propagate")
                print(to_propagate)
                status, clause_index = self.unit_propagation(to_propagate)
                if status == 1 and clause_index != None:
                    # conflict found, do conflict analysis
                    new_decision_level = self.conflict_analysis(clause_index)
                    print(new_decision_level)
                else:
                    # propagated, deciding new variable
                    break

                    #   identify the decision level to backtrack
                    #   if cant (decision level < 0), return None (UNSAT)
                    #   else
                    #       backtrack the assignment,
                    #       decrease the decision level,
                    #       insert the conflict clause after conflict analysis in the clause
                    #       set (next unit propagation will handle the reverse value for
                    #       the variable)

        return self.M
