"""
Pure simulation runner for Game of Life games.

This module provides a single `run_simulation()` function that executes a GOL simulation
and returns the results. It has no I/O side effects - callers are responsible for:
- Obtaining initial conditions (e.g., from gollyx_maps)
- Persisting results (e.g., to filesystem or S3)

This design allows the same simulation logic to be used by:
- gollyx-backend-generator (thread-based, file I/O)
- lambda/life-worker (Lambda-based, S3 I/O)
"""

import time
import logging
from typing import Optional, Callable, List

from .toroidal import ToroidalGOL
from .star import StarGOL

logger = logging.getLogger(__name__)


def run_simulation(
    initial_conditions_1: str,
    initial_conditions_2: str,
    rows: int,
    columns: int,
    cup: str,
    rule_b: List[int],
    rule_s: List[int],
    rule_c: Optional[int] = None,
    fixed_ngenerations: int = 0,
    min_generations: int = 1000,
    max_generations: int = 25000,
    timeout_seconds: int = 3600,
    max_attempts: int = 10,
    initial_conditions_b1: str = "[]",
    initial_conditions_b2: str = "[]",
    initial_conditions_c1: str = "[]",
    initial_conditions_c2: str = "[]",
    log_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Run a Game of Life simulation and return the results.

    This is a pure function with no I/O side effects. The caller is responsible
    for obtaining initial conditions (e.g., from gollyx_maps) and persisting
    results (e.g., to filesystem or S3).

    Args:
        initial_conditions_1: JSON string of team 1 live cells.
            Format: [{"y": [x1, x2, ...]}, ...] where each dict maps a row (y)
            to a list of column positions (x) of live cells.
        initial_conditions_2: JSON string of team 2 live cells (same format).
        rows: Number of rows in the game board.
        columns: Number of columns in the game board.
        cup: Cup type - determines GOL variant. Cups with a "star" prefix
            (e.g., "star-vi") use StarGOL; plain roman numerals (e.g., "vii")
            use ToroidalGOL.
        rule_b: Birth rule (list of neighbor counts that cause birth).
        rule_s: Survival rule (list of neighbor counts that allow survival).
        rule_c: Generations rule (only for 'star' cup) - dead cells wait this
            many generations before they can be reborn.
        fixed_ngenerations: If > 0, stop after this many generations.
        min_generations: Minimum generations before checking for victor.
        max_generations: Maximum generations before giving up on the simulation.
        timeout_seconds: Maximum wall-clock time for simulation.
        max_attempts: Number of retry attempts for ties (only first attempt used
            since we don't have access to new map realizations - caller should
            handle retries with new maps).
        initial_conditions_b1: (Star only) Team 1 dead-but-waiting cells JSON.
        initial_conditions_b2: (Star only) Team 2 dead-but-waiting cells JSON.
        initial_conditions_c1: (Star only) Team 1 color-wait state cells JSON.
        initial_conditions_c2: (Star only) Team 2 color-wait state cells JSON.
        log_callback: Optional callback for logging (signature: callback(message: str)).

    Returns:
        {
            'team1Score': int,      # Live cells for team 1
            'team2Score': int,      # Live cells for team 2
            'generations': int,     # Number of generations run
            'success': bool,        # True if simulation completed without tie
            'tie': bool,            # True if simulation ended in a tie
        }

    Raises:
        ValueError: If cup type is unrecognized
    """

    def log(message: str):
        if log_callback:
            log_callback(message)
        else:
            logger.info(message)

    # Determine GOL variant from cup type:
    # - Peninsula union cups have a "star-" prefix (e.g., "star-vi", "star-xxi")
    #   and use StarGOL (Generations rule variant)
    # - Golly union cups are plain roman numerals (e.g., "vi", "vii", "xxi")
    #   and use ToroidalGOL (standard two-color variant)
    cup_lower = cup.lower()
    is_star = cup_lower.startswith("star")

    # Create GOL instance based on cup type
    # Both ToroidalGOL and StarGOL accept JSON strings directly
    if is_star:
        if rule_c is None:
            raise ValueError("rule_c is required for star cup")
        gol = StarGOL(
            s1=initial_conditions_1,
            s2=initial_conditions_2,
            rows=rows,
            columns=columns,
            rule_b=rule_b,
            rule_s=rule_s,
            rule_c=rule_c,
            b1=initial_conditions_b1,
            b2=initial_conditions_b2,
            c1=initial_conditions_c1,
            c2=initial_conditions_c2,
        )
    else:
        # Cup II and VI use ToroidalGOL
        gol = ToroidalGOL(
            initial_conditions_1,
            initial_conditions_2,
            rows,
            columns,
            rule_b,
            rule_s,
        )

    start = time.time()

    # Run simulation loop
    while True:
        # Check stopping conditions
        if fixed_ngenerations > 0:
            # Fixed generation mode: stop at exact count
            if gol.generation >= fixed_ngenerations:
                break
        else:
            # Victory mode: stop when victor is found
            if not gol.running:
                break

        gol.next_step()

        # Periodic checks every 100 generations
        if gol.generation % 100 == 0:
            elapsed = time.time() - start

            # Timeout check
            if timeout_seconds > 0 and elapsed > timeout_seconds:
                log(f"Simulation timed out after {elapsed:.1f}s at generation {gol.generation}")
                break

            # Max generation check
            if gol.generation >= max_generations:
                log(f"Simulation reached max generation limit ({max_generations})")
                break

            # Progress logging every 1000 generations
            if gol.generation % 1000 == 0:
                log(f"Simulation at generation {gol.generation}")

    # Get final cell counts
    live_counts = gol.get_live_counts()

    # Extract scores based on cup type
    if is_star:
        team1_score = live_counts["liveCellsColors"][0]
        team2_score = live_counts["liveCellsColors"][1]
    else:
        team1_score = live_counts["liveCells1"]
        team2_score = live_counts["liveCells2"]

    # Check for tie
    is_tie = (team1_score == team2_score)

    # Determine success based on conditions
    success = False
    if fixed_ngenerations > 0 and gol.generation >= fixed_ngenerations:
        # Fixed generation mode: success if we reached the target and no tie
        success = not is_tie
    elif not gol.running and gol.generation >= min_generations and not is_tie:
        # Victory mode: success if we passed min generations with a winner
        success = True

    return {
        "team1Score": team1_score,
        "team2Score": team2_score,
        "generations": live_counts["generation"],
        "success": success,
        "tie": is_tie,
    }
