import math

# Namespace matemático seguro (solo funciones/constantes necesarias)
MATH_NAMESPACE = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
MATH_NAMESPACE.update({
    "abs": abs
})

def make_func(expr: str):
    """
    Crea una función f(x) a partir de una expresión tipo string, p. ej. "cos(x) - x".
    Usa eval con un namespace MUY limitado (sin __builtins__).
    """
    expr = expr.strip()
    code = compile(expr, "<expr>", "eval")

    def f(x):
        local_ns = {"x": x}
        return eval(code, {"__builtins__": {}}, {**MATH_NAMESPACE, **local_ns})

    return f


def eval_scalar(expr: str) -> float:
    """
    Evalúa una expresión numérica SIN 'x' usando el mismo namespace matemático seguro.
    Ejemplos válidos: 'pi/4', '1/3', 'sqrt(2)/2', 'e**-3'
    """
    expr = expr.strip()
    code = compile(expr, "<scalar>", "eval")
    return float(eval(code, {"__builtins__": {}}, MATH_NAMESPACE))
