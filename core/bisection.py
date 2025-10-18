from typing import Callable, List, Dict, Tuple

def bisection_with_log(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-6,
    max_iter: int = 60
) -> Tuple[float, List[Dict]]:
    """
    Bisección: requiere f(a)*f(b) < 0
    Registra: iter, Pn (punto medio), f(Pn), error = (b-a)/2
    """
    if a > b:
        a, b = b, a
    fa, fb = f(a), f(b)
    if fa == 0: 
        return a, [{"iter": 0, "Pn": a, "fPn": fa, "error": 0.0}]
    if fb == 0: 
        return b, [{"iter": 0, "Pn": b, "fPn": fb, "error": 0.0}]
    if fa * fb > 0:
        raise ValueError("Bisección: f(a) y f(b) deben tener signos opuestos.")

    log: List[Dict] = []
    for n in range(1, max_iter + 1):
        p = (a + b) / 2.0
        fp = f(p)
        err = (b - a) / 2.0
        log.append({"iter": n, "Pn": p, "fPn": fp, "error": err})
        if err < tol or fp == 0.0:
            return p, log
        # Selección del subintervalo con cambio de signo
        if fa * fp < 0:
            b, fb = p, fp
        else:
            a, fa = p, fp
    return (a + b) / 2.0, log
