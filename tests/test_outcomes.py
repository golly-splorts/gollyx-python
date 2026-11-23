import pytest
from gollyx_python import run_simulation
from .fixtures_outcomes import OUTCOMES


@pytest.mark.parametrize("game", OUTCOMES, ids=[g["name"] for g in OUTCOMES])
def test_outcomes(game):
    """
    Check scores, generations, success and tie of each game against known good results
    """
    assert run_simulation(**game["kwargs"]) == game["expected"]
