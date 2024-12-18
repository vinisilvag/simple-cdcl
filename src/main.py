import sys
from timeit import default_timer as timer

from cdcl import CDCL
from helpers import parse_dimacs_instance


def main():
    if len(sys.argv) != 2:
        print("invalid CLI format")
        sys.exit(1)

    instance = sys.argv[1]
    parsed = parse_dimacs_instance(instance)
    if not parsed:
        print("fail to parse this instance")
        sys.exit(1)

    print("parsed")

    variable_num, clause_num, clauses = parsed
    cdcl = CDCL(variable_num, clause_num, clauses)

    start = timer()
    model = cdcl.solve()
    end = timer()

    if model:
        print("s SATISFIABLE")
        print(model)
    else:
        print("s UNSATISFIABLE")

    print((end - start) * 1000, "ms")

    sys.exit(0)


if __name__ == "__main__":
    main()
