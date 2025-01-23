from collections import defaultdict
from typing import Optional

from helpers import Assignment, Clause, Formula, Literal


class CDCL:
    def __init__(self, variable_num, clause_num, formula):
        self.variable_num: int = variable_num
        self.clause_num: int = clause_num
        self.formula: Formula = formula

        # stack with assignments (convenient push and pop operations)
        self.M: list[Assignment] = []
        # vector with current assignment (convenient O(1) access)
        self.assignment: list[Optional[bool]] = [
            None for _ in range(self.variable_num + 1)
        ]
        # current decision level
        self.decision_level = 0

        # initialize the 2-watched literals data structure
        self.watched_literals: dict[Literal, list[int]] = defaultdict(list)
        for clause_index, clause in enumerate(formula.clauses):
            if len(clause) == 1:
                self.watched_literals[clause.literals[0]].append(clause_index)
            else:
                self.watched_literals[clause.literals[0]].append(clause_index)
                self.watched_literals[clause.literals[1]].append(clause_index)

        # VSIDS
        self.activity: dict[Literal, float] = defaultdict(int)
        self.decay_factor = 0.95
        self.increment = 1
        # initial score is the number of occurrences of the
        # literal in the clauses of the formula
        for clause in self.formula.clauses:
            for literal in clause.literals:
                self.activity[literal] += self.increment

    def apply_decay(self):
        for variable in self.activity:
            self.activity[variable] *= self.decay_factor

    def assign(self, variable: int, value: bool, antecedent: Optional[int]):
        self.M.append(Assignment(self.decision_level, variable, value, antecedent))
        self.assignment[variable] = value

    def unassign(self, literal: int):
        self.assignment[literal] = None
        self.M = [assignment for assignment in self.M if assignment.literal != literal]

    def solve_only_negative_or_positive_literals(self) -> list[Literal]:
        literal_count = defaultdict(int)
        to_propagate = []

        for clause in self.formula.clauses:
            for literal in clause.literals:
                literal_count[literal] += 1
                literal_count[literal.negation()] += 0

        for lit, count in literal_count.items():
            if count > 0 and literal_count[lit.negation()] == 0:
                if self.assignment[lit.variable] == None:
                    self.assign(lit.variable, not lit.is_negated, None)
                    to_propagate.insert(0, lit)

        return to_propagate

    def solve_unit_clauses(self) -> list[Literal]:
        to_propagate = []

        for _, clause in enumerate(self.formula.clauses):
            if len(clause.literals) == 1:
                literal = clause.literals[0]
                if self.assignment[literal.variable] == None:
                    self.assign(literal.variable, not literal.is_negated, None)
                    to_propagate.insert(0, literal)

        return to_propagate

    # can be improved I guess
    def all_clauses_are_satisfied(self) -> bool:
        satisfied = 0
        for clause in self.formula.clauses:
            for literal in clause.literals:
                assignment = self.assignment[literal.variable]
                if assignment != None and (
                    (assignment and not literal.is_negated)
                    or (not assignment and literal.is_negated)
                ):
                    satisfied += 1
                    break
        return satisfied == len(self.formula.clauses)

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
                        # literal already watched (by self or other pointer)
                        continue

                    if self.assignment[lit.variable] == None:
                        # rewatch a non assigned literal
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
                    # get the list of literals watched by that clause
                    literals = [
                        key
                        for key, clauses_watching in self.watched_literals.items()
                        if clause in clauses_watching
                    ]

                    # conflict in an unit clause
                    if len(literals) == 1:
                        return 1, clause

                    # get the other pointer
                    other_watched_literal = (
                        literals[0] if literals[1] == negated_lit else literals[1]
                    )
                    if self.assignment[other_watched_literal.variable] == None:
                        # first pointer is watching False and second None
                        # it means that this clause is an unit clause, propagate too
                        self.assign(
                            other_watched_literal.variable,
                            not other_watched_literal.is_negated,
                            clause,
                        )
                        to_propagate.insert(0, other_watched_literal)
                    else:
                        # second pointer is watching a assigned literal
                        assignment = self.assignment[other_watched_literal.variable]
                        if (assignment and not other_watched_literal.is_negated) or (
                            not assignment and other_watched_literal.is_negated
                        ):
                            # True literal, clause is satisfied, it's fine
                            continue
                        else:
                            # False literal too and can't change the pointer
                            # it means that we have a conflict
                            return 1, clause

        return 0, None

    def choose_literal(self):
        # get the list of candidates (literals not assigned)
        # and insert in the list their negation too
        candidates = []
        for i in range(1, self.variable_num + 1):
            if self.assignment[i] == None:
                literal = Literal(i, False)
                candidates.append(literal)
                candidates.append(literal.negation())

        # sort by the activity map value
        candidates.sort(key=lambda i: self.activity[i], reverse=True)

        # get the candidate with highest activity
        candidate = candidates[0]
        return candidate, not candidate.is_negated

    def resolution(self, c_1: Clause, c_2: Clause, pivot: Literal) -> Clause:
        clause = set(c_1.literals + c_2.literals) - {pivot} - {pivot.negation()}
        return Clause(list(clause))

    def learn(self, clause: Clause):
        # append in the formula
        self.formula.clauses.append(clause)

        # update the watch pointers
        clause_index = self.formula.clauses.index(clause)
        literals = []
        for assignment in self.M:
            for literal in clause.literals:
                if assignment.literal == literal.variable:
                    literals.append((assignment.decision_level, literal))
        literals.sort(key=lambda x: x[0], reverse=True)

        literals_watched = 0

        for literal in literals:
            if literals_watched < 2:
                self.watched_literals[literal].append(clause_index)
                literals_watched += 1

    def backjump(self, new_decision_level: int):
        to_remove = [
            assignment
            for assignment in self.M
            if assignment.decision_level > new_decision_level
        ]
        for assignment in to_remove:
            self.unassign(assignment.literal)

        self.decision_level = new_decision_level

        return to_remove[0]

    def conflict_analysis(self, clause: int) -> tuple[int, Clause]:
        seen = []

        learned_clause = self.formula.clauses[clause]
        literals = [
            assignment
            for assignment in self.M
            if assignment.literal in learned_clause
            and assignment.decision_level == self.decision_level
            and assignment.antecedent != None
        ]

        while len(literals) != 0:
            literal = literals.pop()
            if literal in seen:
                continue
            seen.append(literal)
            learned_clause = self.resolution(
                learned_clause,
                self.formula.clauses[literal.antecedent],
                Literal(literal.literal, not literal.value),
            )
            literals = [
                assignment
                for assignment in self.M
                if assignment.literal in learned_clause
                and assignment.decision_level == self.decision_level
                and assignment.antecedent != None
            ]

        # update activity for literals in the learned clause
        for literal in learned_clause.literals:
            self.activity[literal] += self.increment

        # apply decay
        # currently applying decay at every conflict
        self.apply_decay()

        decision_levels = sorted(
            # list(dict.fromkeys(...)) to remove duplicates
            list(
                dict.fromkeys(
                    [
                        assignment.decision_level
                        for assignment in self.M
                        if assignment.literal in learned_clause
                    ]
                )
            ),
            reverse=True,
        )

        if len(decision_levels) < 2:
            return 0, learned_clause
        else:
            return decision_levels[1], learned_clause

    def solve(self):
        # purify step
        to_propagate = []
        # to_propagate.extend(self.solve_only_negative_or_positive_literals())
        literals_from_unit_clauses = self.solve_unit_clauses()

        to_propagate.extend(literals_from_unit_clauses)

        status, _ = self.unit_propagation(to_propagate)
        # conflict, formula is UNSAT
        if status == 1:
            return None

        while not self.all_clauses_are_satisfied():
            literal, value = self.choose_literal()
            self.decision_level += 1
            self.assign(literal.variable, value, None)
            to_propagate.append(literal)

            while True:
                status, clause_index = self.unit_propagation(to_propagate)
                if status == 1 and clause_index != None:
                    if self.decision_level == 0:
                        # conflict and current decision level is 0
                        # return UNSAT
                        return None

                    # conflict found and decision level != 0, do conflict analysis
                    new_decision_level, conflict_clause = self.conflict_analysis(
                        clause_index
                    )

                    self.learn(conflict_clause)
                    self.backjump(new_decision_level)
                    for literal in conflict_clause.literals:
                        if self.assignment[literal.variable] == None:
                            self.assign(
                                literal.variable,
                                not literal.is_negated,
                                self.formula.clauses.index(conflict_clause),
                            )
                            to_propagate = []
                            to_propagate.append(literal)
                            break
                else:
                    # propagated, deciding new variable in the next iteration
                    break

        return self.M
