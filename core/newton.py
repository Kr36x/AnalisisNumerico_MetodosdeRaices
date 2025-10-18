# newton_app/core/newton.py
from typing import Callable, List, Dict, Tuple

def newton_with_log(
    f: Callable[[float], float],
    df: Callable[[float], float],
    P0: float,
    tol: float = 1e-5,
    max_iter: int = 20
) -> Tuple[float, List[Dict]]:
    """
    Método de Newton-Raphson con bitácora de iteraciones.

    Devuelve (Pn_final, log) donde log es una lista de dicts:
    [{'iter': n, 'Pn': Pn, 'fPn': f(Pn), 'error': |Pn-Pn-1|}, ...]
    """
    log: List[Dict] = []
    Pn_1 = P0
    for n in range(1, max_iter + 1):
        f_val = f(Pn_1)
        df_val = df(Pn_1)
        if df_val == 0:
            raise ValueError("f'(Pn-1) = 0. No se puede continuar con Newton.")
        Pn = Pn_1 - f_val / df_val
        error = abs(Pn - Pn_1)
        log.append({"iter": n, "Pn": Pn, "fPn": f(Pn), "error": error})
        if error < tol:
            return Pn, log
        Pn_1 = Pn
    return Pn_1, log
