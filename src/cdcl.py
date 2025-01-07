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

    def assign(self, variable: int, value: bool):
        self.M.append(Assignment(self.decision_level, variable, value))
        self.assignment[variable] = value
        self.update_two_pointers(variable, value)

    def unassign(self, remove: int):
        self.assignment[self.M[remove].literal] = None
        self.M.pop(remove)

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

            if first_lit.variable == variable:
                print("primeiro lit", first_lit.variable, "igual a variable", variable)
                print("negated?", first_lit.is_negated)
                print("value?", value)
                if (not first_lit.is_negated and not value) or (
                    first_lit.is_negated and value
                ):
                    literals = self.formula.clauses[i].literals
                    for j, literal in enumerate(literals):
                        if (
                            self.assignment[literal.variable] == None
                            and pointers[1] != j
                        ):
                            print("atualizando o primeiro ponteiro pra posicao", j)
                            pointers[0] = j
                            break

            if second_lit.variable == variable:
                print("segundo lit", second_lit.variable, "igual a variable", variable)
                if (not second_lit.is_negated and not value) or (
                    second_lit.is_negated and value
                ):
                    literals = self.formula.clauses[i].literals
                    for j, literal in enumerate(literals):
                        if (
                            self.assignment[literal.variable] == None
                            and pointers[0] != j
                        ):
                            print("atualizando o segundo ponteiro pra posicao", j)
                            pointers[1] = j
                            break

    def solve_only_neg_or_pos_literals(self):
        print("\nliterais apenas positivos ou negativos na formula")
        for variable in list(range(1, self.variable_num + 1)):
            occurs_pos = False
            occurs_neg = False
            for clause in self.formula.clauses:
                for lit in clause.literals:
                    if lit.variable == variable:
                        if lit.is_negated:
                            occurs_neg = True
                        else:
                            occurs_pos = True

            if occurs_pos and not occurs_neg:
                print(variable, "aparece apenas positivamente")
                if self.assignment[variable] == None:
                    self.assign(variable, True)
            elif occurs_neg and not occurs_pos:
                print(variable, "aparece apenas negativamente")
                if self.assignment[variable] == None:
                    self.assign(variable, False)

    def solve_unit_clauses(self):
        print("\nclausulas com apenas um literal...")
        for i, clause in enumerate(self.formula.clauses):
            if len(clause.literals) == 1:
                print("clausula", i, "tem apenas um literal")
                print("assinalando ele...")
                literal = clause.literals[0]
                if literal.is_negated:
                    if self.assignment[literal.variable] == None:
                        self.assign(literal.variable, False)
                else:
                    if self.assignment[literal.variable] == None:
                        self.assign(literal.variable, True)

    def all_variables_assigned(self) -> bool:
        return len(self.M) == self.variable_num

    def can_propagate(self) -> Optional[tuple[int, tuple[Literal, bool]]]:
        print("\nclause and pointers")
        for i, pointers in enumerate(self.two_pointers):
            print("clause", i, "pointers", pointers)
            if not pointers:
                continue

            first_lit = self.formula.clauses[i].literals[pointers[0]]
            second_lit = self.formula.clauses[i].literals[pointers[1]]

            print(
                "first lit", first_lit.is_negated, self.assignment[first_lit.variable]
            )
            print(
                "second lit",
                second_lit.is_negated,
                self.assignment[second_lit.variable],
            )

            # clauses are satisfied
            if not first_lit.is_negated and self.assignment[first_lit.variable] == True:
                continue
            if first_lit.is_negated and self.assignment[first_lit.variable] == False:
                continue

            if (
                not second_lit.is_negated
                and self.assignment[second_lit.variable] == True
            ):
                continue
            if second_lit.is_negated and self.assignment[second_lit.variable] == False:
                continue

            # clauses can be propagated
            if (
                not first_lit.is_negated
                and self.assignment[first_lit.variable] == False
            ):
                if self.assignment[second_lit.variable] == None:
                    return i, (second_lit, not second_lit.is_negated)

            if first_lit.is_negated and self.assignment[first_lit.variable] == True:
                if self.assignment[second_lit.variable] == None:
                    return i, (second_lit, not second_lit.is_negated)

            if (
                not second_lit.is_negated
                and self.assignment[second_lit.variable] == False
            ):
                if self.assignment[first_lit.variable] == None:
                    return i, (first_lit, not first_lit.is_negated)

            if second_lit.is_negated and self.assignment[second_lit.variable] == True:
                if self.assignment[first_lit.variable] == None:
                    return i, (first_lit, not first_lit.is_negated)

        return None

    def unit_propagation(self) -> tuple[int, Optional[int]]:
        has_unit_clause = True
        while has_unit_clause:
            has_unit_clause = False
            clause = self.can_propagate()
            if not clause:
                print("\ncant propagate more")
                continue

            clause_index, literal = clause
            literal, value = literal

            if (
                self.assignment[literal.variable] != None
                and self.assignment[literal.variable] != value
            ):
                print("\nconflict found")
                print(
                    literal.variable,
                    "vale",
                    self.assignment[literal.variable],
                    "e para satisfazer a clausula",
                    clause_index,
                    "deve passar a valer",
                    value,
                )
                return 1, clause_index

            print("\npropagating clause", clause_index)
            print("assinalando", value, "para", literal.variable)
            self.assign(literal.variable, value)

        return 0, None

    def choose_variable(self):
        to_assign = next(literal for literal in self.assignment if literal is not None)
        return to_assign, random.choice([False, True])

    def backjump(self, b: int):
        to_remove = []
        for i, literal in enumerate(self.M):
            if literal.decision_level > b:
                to_remove.append(i)

        for rem in to_remove:
            self.unassign(rem)

    def conflict_analysis(self) -> int:
        return -1

    def solve(self):
        # purify step
        self.solve_only_neg_or_pos_literals()
        self.solve_unit_clauses()

        print("\nafter purify")
        print(self.M)

        print("\n-------------------------------------------------")

        print("\npropagating after purify")
        status, _ = self.unit_propagation()
        # conflict, formula is UNSAT from the beggining
        if status == 1:
            return None

        print("\nafter propagating")
        print(self.M)

        print("\n-------------------------------------------------")

        return None

        print("\nstarting propagation and deciding or end")
        while not self.all_variables_assigned():
            variable, value = self.choose_variable()
            print("\ndeciding:", variable, value)
            self.decision_level += 1
            self.assign(variable, value)

            status, clause_index = self.unit_propagation()
            # conflict found, do conflict analysis
            if status == 1:
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
