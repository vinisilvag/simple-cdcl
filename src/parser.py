from typing import Optional

from helpers import Clause, Formula, Literal


def parse_dimacs_instance(instance: str) -> Optional[tuple[int, int, list[list[int]]]]:
    print("parsing:", instance)

    variable_num: int = 0
    clause_num: int = 0
    clauses = []

    input_file = open(instance, "r")
    if not input_file:
        return None

    curr_clause = []
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
                        end = int(parsed[-1])
                        curr_clause.extend([int(x) for x in parsed])
                        if end == 0:
                            clauses.append(curr_clause[:-1])
                            curr_clause = []

    return variable_num, clause_num, clauses
