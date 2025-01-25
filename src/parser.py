from typing import Optional

from helpers import Clause, Formula, Literal


def parse_dimacs_instance(instance: str) -> Optional[tuple[int, int, Formula]]:
    current_clause = []
    variable_num: int = 0
    clause_num: int = 0
    formula = Formula([])

    input_file = open(instance, "r")
    if not input_file:
        return None

    for line in input_file:
        l = line.strip()
        if not l:
            break

        match l[0]:
            case "c":
                continue
            case "p":
                problem = [x for x in l.split(" ") if x != ""]
                variable_num = int(problem[2])
                clause_num = int(problem[3])
            case _:
                if l[0] == "0":
                    break

                parsed = [x for x in l.split(" ") if x != ""]
                clause_ended = parsed[-1]
                if int(clause_ended) == 0:
                    current_clause.extend(
                        [
                            (
                                Literal(abs(int(x)), False)
                                if int(x) > 0
                                else Literal(abs(int(x)), True)
                            )
                            for x in parsed[:-1]
                        ]
                    )
                    formula.clauses.append(Clause(current_clause))
                    current_clause = []
                else:
                    current_clause.extend(
                        [
                            (
                                Literal(abs(int(x)), False)
                                if int(x) > 0
                                else Literal(abs(int(x)), True)
                            )
                            for x in parsed[:]
                        ]
                    )

    return variable_num, clause_num, formula
