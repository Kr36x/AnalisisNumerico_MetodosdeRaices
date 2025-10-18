# analisisNumerico_app/core/derivative.py

def numeric_derivative(f, h: float = 1e-6):
    """Derivada numérica por diferencias centrales."""
    def df(x):
        return (f(x + h) - f(x - h)) / (2 * h)
    return df

__all__ = ["numeric_derivative"]
