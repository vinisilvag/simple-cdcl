import random
import sys
from typing import Optional

from helpers import Assignment, Formula


class CDCL:
    def __init__(self, variable_num, clause_num, formula):
        self.variable_num: int = variable_num
        self.clause_num: int = clause_num
        self.formula: Formula = formula

        self.two_pointers = [
            [0, 1] if len(clause.literals) >= 2 else None for clause in formula.clauses
        ]

    # can be improved I guess
    def purify(self, assignment: list[Assignment]):
        for variable in list(range(1, self.variable_num + 1)):
            occurs_pos = False
            occurs_neg = False

            for clause in self.formula.clauses:
                for lit in clause.literals:
                    if lit.lit == variable:
                        if lit.is_negated:
                            occurs_neg = True
                        else:
                            occurs_pos = True
            if occurs_pos and not occurs_neg:
                assignment.append(Assignment(0, variable, True))
            elif occurs_neg and not occurs_pos:
                assignment.append(Assignment(0, variable, False))

    def all_variables_assigned(self, assignment: list[Assignment]) -> bool:
        assigned = [x.literal for x in assignment]
        to_assign = list(set(list(range(1, self.variable_num + 1))) - set(assigned))
        return len(to_assign) == 0

    # two pointers for this
    def can_propagate(self, assignment: list[Assignment]) -> Optional[int]:
        for pointers in self.two_pointers:
            if not pointers:
                continue

            # check if first pointer points to an falsified assignment
            # and second not or vice-versa

            # if yes, can propagate this clause

        return None

    def propagate(self, assignment: list[Assignment]):
        while True:
            clause = self.can_propagate(assignment)
            if not clause:
                break

            print("propagating clause", clause)
            # append to assignment
            # update two_pointers

    # do better variable selection later
    def choose_variable(self, assignment: list[Assignment]):
        assigned = [x.literal for x in assignment]
        to_assign = list(set(list(range(1, self.variable_num + 1))) - set(assigned))
        return to_assign[0], random.choice([False, True])

    def conflict_analysis(self) -> int:
        return -1

    def solve(self):
        assignment: list[Assignment] = []
        decision_level = 0

        # assign variables that appears only positively or negatively in the formula
        self.purify(assignment)

        status = self.propagate(assignment)
        # conflict, formula is UNSAT from the beggining
        if status == 1:
            return None

        while not self.all_variables_assigned(assignment):
            variable, value = self.choose_variable(assignment)
            decision_level += 1
            assignment.append(Assignment(decision_level, variable, value))

            propagate = self.propagate(assignment)
            # conflict found, do conflict analysis
            if propagate == 1:
                new_decision_level = self.conflict_analysis()
                if new_decision_level < 0:
                    return None

                #   identify the decision level to backtrack
                #   if cant (decision level < 0), return None (UNSAT)
                #   else
                #       backtrack the assignment,
                #       decrease the decision level,
                #       insert the conflict clause after conflict analysis in the clause
                #       set (next unit propagation will handle the reverse value for
                #       the variable)
                pass

        return assignment
