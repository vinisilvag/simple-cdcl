# simple-cdcl

A simple implementation of the Conflict-Driven Clause Learning (CDCL) framework for solving SAT problems.

This project was developed as part of the course Theory and Practice of SMT Solving at UFMG.

---

## Prerequisites
Before proceeding, ensure you have the following installed:

- **Python** (version 3.12 or higher)
- **uv** (Rust-based project manager)

---

## Installation

1. **Install `uv`**:
   If you don’t have `uv` installed, you can install it using `wget`:
   ```bash
   wget -qO- https://astral.sh/uv/install.sh | sh
   ```

2. **Check if `uv` is installed correctly**:
   After installing, you can check that `uv` is available by running the `uv` command:
   ```bash
   uv 
   ```

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/vinisilvag/simple-cdcl.git
   cd simple-cdcl
   ```

4. **Install dependencies with `uv`**:
   ```bash
   uv sync
   ```
   This command will install all the dependencies specified in your `pyproject.toml` file.

---

## Running the Application

1. **Run the Application**:
   ```bash
   uv run src/main.py "./path/to/the-instance.cnf"
   ```

---

## Project Structure

```
simple-cdcl/
├── benchmarks          # Benchmark problems
│   └── results         # Results of the benchmarks
│       ├── minisat     # Outputs of MiniSat
│       ├── solver      # Outputs of the solution
│       └── output.csv  # Generated .csv with the measured information
│   └── sat             # SAT instances
│       └── ...
│   └── unsat           # UNSAT instances
│       └── ...
├── binaries            # Binaries used (MiniSat)
│   └── minisat         # MiniSat 2.2 binary
├── examples            # Simple examples for debugging
│   └── cadical         # Some CaDiCaL tests
│       └── ...
│   └── satlib          # Some SATLIB tests
│       └── ...
│   └── other           # Other tests
│       └── ...
├── src                 # Source code of the application
│   ├── cdcl.py         # CDCL and related implementations
│   ├── helpers.py      # Dataclass implementations
│   ├── main.py         # Entry point of the application
│   └── parser.py       # DIMACS CNF parser implementation
├── LICENSE             # License file
├── pyproject.toml      # Project configuration file
├── report.pdf          # Implementation report
├── README.md           # Project documentation
├── analysis.ipynb      # Python Notebook to analyze the benchmark data
├── run.sh              # Script for running MiniSat on the benchmarks
└── uv.lock             # uv lock file
└── ...
```

---

## Contributing
Feel free to open issues or submit pull requests if you'd like to contribute to this project.

---

## License
This project is licensed under the [MIT License](LICENSE).
