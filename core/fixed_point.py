from typing import Callable, List, Dict, Tuple

def fixed_point_with_log(
    g: Callable[[float], float],
    P0: float,
    tol: float = 1e-5,
    max_iter: int = 50
) -> Tuple[float, List[Dict]]:
    """
    Iteración de punto fijo: Pn = g(Pn-1)
    Registra: iter, Pn, fPn (no aplica → NaN), error = |Pn - Pn-1|
    """
    import math
    log: List[Dict] = []
    Pn_1 = P0
    for n in range(1, max_iter + 1):
        Pn = g(Pn_1)
        error = abs(Pn - Pn_1)
        log.append({"iter": n, "Pn": Pn, "fPn": math.nan, "error": error})
        if error < tol:
            return Pn, log
        Pn_1 = Pn
    return Pn_1, log
