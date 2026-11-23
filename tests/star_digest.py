import hashlib
import json


def star_state_digest(gol):
    """
    Hash the full state of a StarGOL: live cells by color and dead-wait cells by phase and color.

    Args:
        gol (StarGOL): simulator to hash.

    Returns:
        str: sha256 hex digest of the sorted cell coordinates.
    """
    live = [sorted(cells) for cells in gol.get_live_cells()]
    dead_wait = [[sorted(cells) for cells in phase] for phase in gol.get_dead_wait_cells()]
    payload = json.dumps({"live": live, "dead_wait": dead_wait}, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()
