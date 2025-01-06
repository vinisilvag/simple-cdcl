import random
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
        self.two_pointers: list[Optional[list[int]]] = [
            [0, 1] if len(clause.literals) >= 2 else None for clause in formula.clauses
        ]

    def update_two_pointers(self, variable: int, value: bool):
        print("\natualizando ponteiros")
        for i, pointers in enumerate(self.two_pointers):
            if not pointers:
                continue

            first_lit = self.formula.clauses[i].literals[pointers[0]]
            second_lit = self.formula.clauses[i].literals[pointers[1]]

            print("\natualizando os ponteiros da clausula", i)
            print(variable, value)
            print(first_lit, second_lit)

            if first_lit.lit == variable:
                print("primeiro lit", first_lit.lit, "igual a variable", variable)
                print("negated?", first_lit.is_negated)
                print("value?", value)
                if (not first_lit.is_negated and not value) or (
                    first_lit.is_negated and value
                ):
                    literals = self.formula.clauses[i].literals
                    for j, literal in enumerate(literals):
                        if self.assignment[literal.lit] == None and pointers[1] != j:
                            print("atualizando o primeiro ponteiro pra posicao", j)
                            self.two_pointers[i][0] = j
                            break
            if second_lit.lit == variable:
                print("segundo lit", second_lit.lit, "igual a variable", variable)
                if (not second_lit.is_negated and not value) or (
                    second_lit.is_negated and value
                ):
                    literals = self.formula.clauses[i].literals
                    for j, literal in enumerate(literals):
                        if self.assignment[literal.lit] == None and pointers[0] != j:
                            print("atualizando o segundo ponteiro pra posicao", j)
                            self.two_pointers[i][1] = j
                            break

    # can be improved I guess
    def purify(self):
        print("\nclausulas com apenas um literal...")
        # purify clauses that has just one literal
        for i, clause in enumerate(self.formula.clauses):
            if len(clause.literals) == 1:
                print("clausula", i, "tem apenas um literal")
                print("assinalando ele...")
                literal = clause.literals[0]
                if literal.is_negated:
                    self.M.append(Assignment(0, literal.lit, False))
                    self.assignment[literal.lit] = False
                    self.update_two_pointers(literal.lit, False)
                else:
                    self.M.append(Assignment(0, literal.lit, True))
                    self.assignment[literal.lit] = True
                    self.update_two_pointers(literal.lit, True)

        print("\nliterais apenas positivos ou negativos na formula")
        # purify variables that appear only positively or negatively
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
                print(variable, "aparece apenas positivamente")
                self.M.append(Assignment(0, variable, True))
                self.assignment[variable] = True
                self.update_two_pointers(variable, True)
            elif occurs_neg and not occurs_pos:
                print(variable, "aparece apenas negativamente")
                self.M.append(Assignment(0, variable, False))
                self.assignment[variable] = False
                self.update_two_pointers(variable, False)

    # check with assignment instead of M?
    def all_variables_assigned(self) -> bool:
        assigned = [x.literal for x in self.M]
        to_assign = list(set(list(range(1, self.variable_num + 1))) - set(assigned))
        return len(to_assign) == 0

    def can_propagate(self) -> Optional[tuple[int, tuple[Literal, bool]]]:
        print("\nclause and pointers")
        for i, pointers in enumerate(self.two_pointers):
            print("clause", i, "pointers", pointers)
            if not pointers:
                continue

            # check if first pointer points to an falsified assignment
            # and second not or vice-versa
            first_lit = self.formula.clauses[i].literals[pointers[0]]
            second_lit = self.formula.clauses[i].literals[pointers[1]]

            # clauses are satisfied
            if not first_lit.is_negated and self.assignment[first_lit.lit] == True:
                continue
            if first_lit.is_negated and self.assignment[first_lit.lit] == False:
                continue
            if not second_lit.is_negated and self.assignment[second_lit.lit] == True:
                continue
            if second_lit.is_negated and self.assignment[second_lit.lit] == False:
                continue

            # clauses can be propagated
            if not first_lit.is_negated and self.assignment[first_lit.lit] == False:
                if self.assignment[second_lit.lit] == None:
                    return i, (second_lit, not second_lit.is_negated)
            if first_lit.is_negated and self.assignment[first_lit.lit] == True:
                if self.assignment[second_lit.lit] == None:
                    return i, (second_lit, not second_lit.is_negated)
            if not second_lit.is_negated and self.assignment[second_lit.lit] == False:
                if self.assignment[first_lit.lit] == None:
                    return i, (first_lit, not first_lit.is_negated)
            if second_lit.is_negated and self.assignment[second_lit.lit] == True:
                if self.assignment[first_lit.lit] == None:
                    return i, (first_lit, not first_lit.is_negated)

        return None

    def propagate(self):
        while True:
            clause = self.can_propagate()
            if not clause:
                print("\ncant propagate more")
                break

            _, literal = clause
            literal, value = literal

            print("\npropagating clause", clause)
            self.M.append(Assignment(self.decision_level, literal.lit, value))
            self.assignment[literal.lit] = value
            self.update_two_pointers(literal.lit, value)

    # do better variable selection later
    # check with assignment instead of M?
    def choose_variable(self):
        assigned = [x.literal for x in self.M]
        to_assign = list(set(list(range(1, self.variable_num + 1))) - set(assigned))
        return to_assign[0], random.choice([False, True])

    def conflict_analysis(self) -> int:
        return -1

    def solve(self):
        # assign variables that appears only positively or negatively in the formula
        self.purify()

        print("\nafter purify")
        print(self.M)

        print("\npropagating after purify")
        status = self.propagate()
        # conflict, formula is UNSAT from the beggining
        if status == 1:
            return None

        print("\nstarting propagation and deciding or end")
        while not self.all_variables_assigned():
            variable, value = self.choose_variable()
            print("\ndeciding:", variable, value)
            self.decision_level += 1
            self.M.append(Assignment(self.decision_level, variable, value))
            self.assignment[variable] = value
            self.update_two_pointers(variable, value)

            propagate = self.propagate()
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

        return self.M
