# gollyx-python

Python implementation of cellular autonoma for GollyX.

Provides a collection of Python classes for simulating various two-dimensional cellular automata, with a focus on
Conway's Game of Life and its multi-team variants. It features several distinct simulation engines, each with
different data structures, performance characteristics, and support for different grid topologies and rulesets.

## Core Functionality

The library is structured around two main types of classes: **Manager Classes** and **Life Simulator Classes**.

### Manager Classes (`manager.py`)

The manager classes are the primary user-facing components. They act as wrappers that simplify the process of
configuring and running a simulation. Users instantiate a manager class, providing parameters such as grid
dimensions, rules, and initial conditions for each team. The manager then creates and controls the appropriate
underlying life simulator instance.

The main responsibilities of a manager class are:
- Loading and parsing configuration (e.g., initial patterns from JSON).
- Instantiating the correct life simulator class.
- Providing a simple interface to the simulation, typically with methods like `next_step()` to advance the
  simulation by one generation and `count()` to retrieve statistics.

The primary manager classes are:
- `ToroidalGOL`: Manages a standard two-team Game of Life on a periodic (toroidal) grid.
- `HellmouthGOL`: Manages a two-team Game of Life using a high-performance, linked-list-based engine.
- `KleinGOL`: Manages a two-team Game of Life on a Klein bottle topology.
- `StarGOLGenerations`: Manages a complex, multi-state cellular automaton with "Generations" rules, where dead
  cells must "rest" for a number of turns before they can be reborn.
- `RainbowGOL`: Manages a four-team variant of the Game of Life.

### Life Simulator Classes

These classes contain the core logic for the cellular automata. They manage the state of the grid and implement the algorithms for evolving it from one generation to the next. There are several distinct implementations, each with different characteristics.

#### `pylife.ToroidalBinaryLife`

- **Purpose**: A two-team (binary) Game of Life simulator on a toroidal grid (periodic boundary conditions).
- **Data Structure**: Represents the grid as a sorted list of rows, where each row is a list containing the
  y-coordinate followed by all the x-coordinates of live cells (e.g., `[y, x1, x2, x3, ...]`). This is simple but
  can be inefficient for very sparse patterns.
- **Interaction**: Instantiated and controlled by the `ToroidalGOL` manager. The manager forwards calls to its
  `next_generation()` and `get_live_counts()` methods.

#### `hellmouthlife.HellmouthBinaryLife`

- **Purpose**: A highly optimized two-team Game of Life simulator.
- **Data Structure**: Uses a sophisticated data structure composed of custom linked lists (`LifeList`,
  `SortedRowList`). This avoids the overhead of Python lists and is designed for high performance, especially with
  sparse cell patterns.
- **Interaction**: Instantiated and controlled by the `HellmouthGOL` manager. This class is more self-contained
  than `ToroidalBinaryLife`; it has its own `LifeStats` inner class that manages statistics and calculates victory
  conditions based on a moving average of population dynamics. The manager primarily interacts with the
  `next_step()` and `get_stats()` methods.

#### `kleinlife.KleinBinaryLife`

- **Purpose**: Simulates a two-team Game of Life on a **Klein bottle**.
- **Data Structure**: Uses the same list-of-lists structure as `ToroidalBinaryLife`.
- **Key Difference**: Its uniqueness lies in the handling of boundary conditions. When a pattern wraps around the
  top/bottom edges, its x-coordinates are inverted (`columns - x - 1`), creating the characteristic twist of a
  Klein bottle.
- **Interaction**: Instantiated and controlled by the `KleinGOL` manager.

#### `starlife.StarBinaryGenerationsCA`

- **Purpose**: Simulates a more complex cellular automaton based on the "Generations" ruleset, which is distinct from Conway's Game of Life.
- **Key Differences**:
    1.  **Multi-State Cells**: Cells are not just "alive" or "dead". When a live cell dies, it enters a "dead wait"
        state for a number of generations (`rule_c`) before it can be reborn.
    2.  **Three Colors**: It supports two competing teams and a third "referee" color for cells born from ties.
    3.  **Rules**: It uses separate rules for Birth (`rule_b`) and Survival (`rule_s`).
- **Data Structure**: Represents the grid very differently from the other simulators. It uses `set` objects
  containing string representations of coordinates (e.g., `"(x,y)"`) to track the state of each color, providing
  fast lookups.
- **Interaction**: Instantiated and controlled by the `StarGOLGenerations` manager.

## Relationships and Interactions

The pattern of interaction is consistent across the library:

1.  A user chooses a **Manager Class** (e.g., `HellmouthGOL`) based on the desired rules and topology.
2.  The user provides configuration (grid size, initial patterns) to the manager's constructor.
3.  The manager's `create_life()` method instantiates the corresponding **Life Simulator Class** (e.g.,
    `HellmouthBinaryLife`), passing it the parsed configuration.
4.  When the user calls `next_step()` on the manager, the manager calls the corresponding `next_step()` or
    `next_generation()` method on its internal `life` object.
5.  The life simulator updates the grid state according to its specific rules and data structures.
6.  The manager retrieves updated statistics by calling a counting method on the `life` object (e.g., `get_stats()`, `get_live_counts()`).

