from typing import Optional


def parse_dimacs_instance(instance: str) -> Optional[tuple[int, int, list[list[int]]]]:
    print("parsing:", instance)

    variable_num: int = 0
    clause_num: int = 0
    clauses: list[list[int]] = []

    with open(instance, "r") as input_file:
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
                            clause = [int(x) for x in parsed[:-1]]
                            clauses.append(clause)

        return variable_num, clause_num, clauses
