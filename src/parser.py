from typing import Optional

from helpers import Clause, Formula, Literal


def parse_dimacs_instance(instance: str) -> Optional[tuple[int, int, Formula]]:
    print("parsing:", instance)

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
                match l:
                    case "0":
                        break
                    case "%":
                        break
                    case _:
                        parsed = [x for x in l.split(" ") if x != ""]
                        formula.clauses.append(
                            Clause(
                                [
                                    (
                                        Literal(abs(int(x)), False)
                                        if int(x) > 0
                                        else Literal(abs(int(x)), True)
                                    )
                                    for x in parsed[:-1]
                                ]
                            )
                        )

    return variable_num, clause_num, formula
