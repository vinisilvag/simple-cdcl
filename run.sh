#!/bin/bash

echo "SAT instances:"
for instance_path in benchmarks/sat/*.cnf; do
  instance=${instance_path##*/}
  echo "Running my implementation and MiniSat on $instance..."

  echo "Running my implementation..."
  timeout 20m uv run src/main.py "benchmarks/sat/$instance" >> "benchmarks/results/solver/sat/$instance.txt"
  EXIT_STATUS=$?
  if [ $EXIT_STATUS -eq 124 ]
  then
    echo "Timeout :("
  else
    echo "Success!"
  fi

  echo "Running MiniSat"
  ./binaries/minisat "benchmarks/sat/$instance" >> "benchmarks/results/minisat/sat/$instance.txt"
done
echo

echo "UNSAT instances:"
for instance_path in benchmarks/unsat/*.cnf; do
  instance=${instance_path##*/}
  echo "Running my implementation and MiniSat on $instance..."

  echo "Running my implementation..."
  timeout 10m uv run src/main.py "benchmarks/unsat/$instance" >> "benchmarks/results/solver/unsat/$instance.txt"
  EXIT_STATUS=$?
  if [ $EXIT_STATUS -eq 124 ]
  then
    echo "Timeout :("
  else
    echo "Success!"
  fi

  echo "Running MiniSat"
  ./binaries/minisat "benchmarks/unsat/$instance" >> "benchmarks/results/minisat/unsat/$instance.txt"
done
echo
