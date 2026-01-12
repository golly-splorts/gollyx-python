# Building and Running the Cython Version

This branch contains a Cython implementation of the GollyX cellular automata engines, designed for significantly improved performance over the pure Python versions.

## Prerequisites

Before building, ensure you have the following installed:

*   **Python 3.x**
*   **C Compiler**: A C compiler is required to compile the generated C code.
    *   **macOS**: Install Xcode Command Line Tools (`xcode-select --install`).
    *   **Linux**: Install GCC (e.g., `sudo apt install build-essential`).
    *   **Windows**: Install "Desktop development with C++" workload via Visual Studio Build Tools.
*   **Build Tools**: `pip`, `setuptools`, `wheel`.

## Building the Extension

You can build the extension modules in-place for development or install the package into your environment.

### Option 1: In-Place Build (Recommended for Development)

This method compiles the `.pyx` files into shared objects (`.so` or `.pyd`) directly in the source tree, making them importable.

1.  Install build dependencies:
    ```bash
    pip install Cython numpy setuptools
    ```

2.  Run the build command (using the provided Makefile):
    ```bash
    make build
    ```
    
    *Alternatively, run the cythonize command directly:*
    ```bash
    cythonize -3 -i src/gollyx_python/*.pyx
    ```

### Option 2: Install Package

To install the package and build the extensions automatically:

```bash
pip install .
```

For an editable install (useful if you plan to modify Python files, though you must rebuild extensions if `.pyx` files change):

```bash
pip install -e .
```

## Running the Code

Once built, the optimized classes are exposed directly via the `gollyx_python` package.

### Available Classes

*   `ToroidalGOL`: An optimized engine for standard two-team Game of Life on a toroidal grid.
*   `StarGOL`: An optimized engine for "Generations" rules (Star Wars, etc.) with multi-state cells.

### Example Usage: ToroidalGOL

Create a file named `run_cython_gol.py` to test the installation:

```python
from gollyx_python import ToroidalGOL

# Define initial conditions
# Format: List of dictionaries, where each dict represents a row.
# Key: Row index (string), Value: List of column indices (integers).

# Team 1: A "Blinker" pattern (horizontal line of 3)
# Row 5, columns 4, 5, 6
initial_state_team1 = [
    {"5": [4, 5, 6]}
]

# Team 2: Empty
initial_state_team2 = []

# Simulation Parameters
rows = 10
columns = 10
birth_rule = [3]        # Standard Life: Born with 3 neighbors
survival_rule = [2, 3]  # Standard Life: Survives with 2 or 3 neighbors

# Initialize the engine
gol = ToroidalGOL(
    s1=initial_state_team1,
    s2=initial_state_team2,
    rows=rows,
    columns=columns,
    rule_b=birth_rule,
    rule_s=survival_rule,
    periodic=True
)

print(f"Initial State - Generation {gol.generation}")
live1, live2 = gol.get_live_cells()
print(f"Team 1 Cells: {live1}")

# Advance one generation
gol.next_generation()

print(f"\nAfter Step 1 - Generation {gol.generation}")
live1, live2 = gol.get_live_cells()
print(f"Team 1 Cells: {live1}")
# Expected output: Cells should be at (5, 5), (5, 4), (5, 6) -> (vertical blinker if standard rules applied differently, 
# but effectively (4,5), (5,5), (6,5) if x/y swapped, or just rotated locally).
```

### Running the Example

```bash
python3 run_cython_gol.py
```

## Troubleshooting

*   **ImportError: No module named 'gollyx_python'**: Ensure you are in the directory containing `src` (if using in-place build) or that you have installed the package.
*   **ModuleNotFoundError: No module named 'gollyx_python.toroidal'**: The extension was not built successfully. Check the output of `make build` for compilation errors.
