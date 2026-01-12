# GollyX C Implementation

This directory contains a C implementation of the GollyX cellular automata simulation engines (Toroidal Game of Life and Star Wars). It is designed to be significantly faster than the Python implementation.

## 1. Compilation

To compile the program, navigate to this directory and use `make`:

```bash
cd src/gollyx_c
make
```

This will produce an executable named `gollyx_c`.

To clean up build artifacts:

```bash
make clean
```

## 2. Testing

A Python test suite is provided to verify the correctness of the C implementation against known "gold" values from the Python/JS implementations.

From the project root directory:

```bash
python3 tests/test_c_impl.py
```

This script automatically compiles the C code (if needed) and runs simulations using test JSON inputs, checking the output for accuracy.

## 3. Running

The program accepts a single argument: the path to a JSON configuration file containing the simulation parameters.

```bash
./gollyx_c <path_to_input.json>
```

### Input Format

The input JSON should contain the following keys (example):

```json
{
  "rows": 100,
  "columns": 120,
  "initialConditions1": "[\"{\\\"30\\\":[50,51,54,55,56]}\", ... ]",
  "initialConditions2": "[\"{\\\"90\\\":[25]}\", ... ]",
  "rule_b": "3",
  "rule_s": "23",
  "halt": true,
  "maxdim": 280,
  "periodic": true
}
```

For "Star Wars" rules, additional keys like `initialConditionsb1`, `rule_c`, etc., are required.

### Output

The program outputs the final simulation state statistics in JSON format to `stdout`.

```json
{
  "generation": 3364,
  "liveCells": 689,
  "liveCells1": 132,
  "liveCells2": 557,
  "victoryPct": 80.841800,
  "coverage": 1.913889,
  "found_victor": true,
  "who_won": 2
}
```

Progress and debug information may be printed to `stderr`.

### Constraints

- **Max Steps**: The simulation is hard-coded to stop after **20,000 generations** (`MAX_TOTAL_STEPS`).
- **Timeout**: The simulation will automatically terminate if it runs for more than **4 minutes**.

```