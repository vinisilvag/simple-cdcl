import sys
from parser import parse_dimacs_instance
from timeit import default_timer as timer

from cdcl import CDCL
from helpers import print_assignment


def main():
    if len(sys.argv) != 3:
        print("Invalid CLI format.")
        print(
            "Expected usage:",
            "`uv run src/main.py benchmark`, or",
            "`uv run src/main.py solve <instance>`",
        )
        sys.exit(1)

    command = sys.argv[1]
    match command:
        case "solve":
            instance = sys.argv[2]
            parsed_instance = parse_dimacs_instance(instance)
            if not parsed_instance:
                print("Fail to parse this instance.")
                sys.exit(1)

            variable_num, clause_num, formula = parsed_instance
            cdcl = CDCL(variable_num, clause_num, formula)

            start = timer()
            model = cdcl.solve()
            end = timer()

            if model:
                print("s SATISFIABLE")
                print("v", end=" ")
                print_assignment(model)
                print()
            else:
                print("s UNSATISFIABLE")

            print((end - start) * 1000, "ms")
        case "benchmark":
            print("Running benchmarks...")
            # run
            print('Benchmarks saved on "bench.csv"!')
        case _:
            print('Invalid <command> option, expected "solve" or "benchmark".')
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
