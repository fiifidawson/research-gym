"""Checks for module 02 - Autograd from scratch.

Read this file. It is the spec. If a check's name and its code disagree, the
code wins, and that is a bug worth an issue.
"""

from __future__ import annotations

from gym.checks import (
    CORE,
    STRETCH,
    Check,
    CheckSuite,
    assert_close,
    assert_equal,
    require,
)


def _value(m):
    """Get the Value class from the module."""
    return require(m, "Value")


# --- core checks -----------------------------------------------------------------


def value_stores_data_and_gradient(m):
    """Check: Value stores data and initializes gradient to 0."""
    Value = _value(m)
    v = Value(5.0)
    assert_close(v.data, 5.0, "Value.data")
    assert_close(v.grad, 0.0, "Value.grad starts at 0")


def value_can_add_two_values(m):
    """Check: Value(2) + Value(3) = 5."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a + b
    assert_close(c.data, 5.0, "Value(2) + Value(3)")


def addition_creates_graph_structure(m):
    """Check: After c = a + b, c remembers its children and operation."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a + b

    if not ((c._children == (a, b)) or (c._children == (b, a))):
        raise AssertionError(
            f"c._children should be (a, b) or (b, a), got {c._children}"
        )

    assert_equal(c._op, "add", "c._op after addition")


def value_can_multiply_two_values(m):
    """Check: Value(2) * Value(3) = 6."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a * b
    assert_close(c.data, 6.0, "Value(2) * Value(3)")


def multiplication_creates_graph_structure(m):
    """Check: After c = a * b, c remembers operation 'mul'."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a * b

    if not ((c._children == (a, b)) or (c._children == (b, a))):
        raise AssertionError(
            f"c._children should be (a, b) or (b, a), got {c._children}"
        )

    assert_equal(c._op, "mul", "c._op after multiplication")


def backward_computes_gradients_for_addition(m):
    """Check: c = a + b; c.backward() gives a.grad = 1, b.grad = 1."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a + b
    c.backward()

    assert_close(a.grad, 1.0, "a.grad after backward for addition")
    assert_close(b.grad, 1.0, "b.grad after backward for addition")


def backward_computes_gradients_for_multiplication(m):
    """Check: c = a * b; c.backward() gives correct gradients."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a * b
    c.backward()

    assert_close(a.grad, 3.0, "a.grad (should be b) after multiplication backward")
    assert_close(b.grad, 2.0, "b.grad (should be a) after multiplication backward")


def backward_accumulates_gradients_on_reused_nodes(m):
    """Check: When a node appears twice, gradients accumulate."""
    Value = _value(m)
    a = Value(2)
    b = a + a
    b.backward()

    assert_close(a.grad, 2.0, "a.grad should accumulate: 1 + 1 = 2")


def backward_works_through_complex_graphs(m):
    """Check: Backward pass through multiple operations."""
    Value = _value(m)
    a = Value(2)
    b = Value(3)
    c = a + b
    d = a * b
    e = c + d
    e.backward()

    assert_close(a.grad, 4.0, "a.grad in complex graph: 1 + 3 = 4")
    assert_close(b.grad, 3.0, "b.grad in complex graph: 1 + 2 = 3")


def value_supports_multiplication_with_scalars(m):
    """Check: Value(2) * 5 = 10."""
    Value = _value(m)
    v = Value(2)
    result = v * 5
    assert_close(result.data, 10.0, "Value(2) * 5")


def reverse_multiplication_works(m):
    """Check: 5 * Value(2) = 10 (tests __rmul__)."""
    Value = _value(m)
    v = Value(2)
    result = 5 * v
    assert_close(result.data, 10.0, "5 * Value(2)")


def value_supports_power_operation(m):
    """Check: Value(3) ** 2 = 9."""
    Value = _value(m)
    v = Value(3)
    result = v ** 2
    assert_close(result.data, 9.0, "Value(3) ** 2")


def backward_computes_power_gradient(m):
    """Check: y = x**2; y.backward() gives x.grad = 2*x."""
    Value = _value(m)
    x = Value(3)
    y = x ** 2
    y.backward()

    assert_close(x.grad, 6.0, "gradient of x^2 at x=3 is 2*3=6")


def value_supports_negation(m):
    """Check: -Value(5) = -5."""
    Value = _value(m)
    v = Value(5)
    result = -v
    assert_close(result.data, -5.0, "-Value(5)")


def value_supports_subtraction(m):
    """Check: Value(5) - Value(2) = 3."""
    Value = _value(m)
    a = Value(5)
    b = Value(2)
    result = a - b
    assert_close(result.data, 3.0, "Value(5) - Value(2)")


def backward_works_through_subtraction(m):
    """Check: Subtraction gradients work correctly."""
    Value = _value(m)
    a = Value(5)
    b = Value(2)
    c = a - b
    c.backward()

    assert_close(a.grad, 1.0, "a.grad for subtraction")
    assert_close(b.grad, -1.0, "b.grad for subtraction")


def value_supports_division(m):
    """Check: Value(10) / Value(2) = 5."""
    Value = _value(m)
    a = Value(10)
    b = Value(2)
    result = a / b
    assert_close(result.data, 5.0, "Value(10) / Value(2)", tol=1e-4)


def repr_shows_data_and_gradient(m):
    """Check: repr(Value) shows both data and gradient."""
    Value = _value(m)
    v = Value(5.0)
    v.grad = 2.0
    repr_str = repr(v)

    if "5" not in repr_str or "2" not in repr_str:
        raise AssertionError(
            f"repr should show data and grad, got: {repr_str}"
        )


# --- stretch checks --------------------------------------------------------------


def backward_gradients_match_finite_differences(m):
    """Check: Gradients match numerical approximation (finite differences)."""
    Value = _value(m)

    def numerical_grad(f, x, eps=1e-5):
        x_plus = Value(x.data + eps)
        x_minus = Value(x.data - eps)
        return (f(x_plus).data - f(x_minus).data) / (2 * eps)

    x = Value(3.0)
    y = x ** 2
    y.backward()

    num_grad = numerical_grad(lambda v: v ** 2, x)
    assert_close(x.grad, num_grad, "analytic vs numeric gradient", tol=1e-4)


def value_supports_reverse_subtraction(m):
    """Check: 10 - Value(3) works (tests __rsub__)."""
    Value = _value(m)
    v = Value(3)
    result = 10 - v
    assert_close(result.data, 7.0, "10 - Value(3)")


def value_supports_complex_nested_expressions(m):
    """Check: Complex expressions work, e.g., (a + b) * (a - b)."""
    Value = _value(m)
    a = Value(5)
    b = Value(3)

    result = (a + b) * (a - b)
    assert_close(result.data, 16.0, "(a+b)*(a-b) where a=5, b=3")

    result.backward()
    assert isinstance(a.grad, float), "gradients should be computed"


SUITE = CheckSuite(
    entrypoint="autograd.py",
    checks=[
        Check(
            "Value stores data and initializes gradient to 0",
            value_stores_data_and_gradient,
            CORE,
        ),
        Check(
            "Value can add two values",
            value_can_add_two_values,
            CORE,
            hint="Implement __add__ to create a new Value with sum of data",
        ),
        Check(
            "Addition creates proper graph structure",
            addition_creates_graph_structure,
            CORE,
            hint="Store _children and _op when creating output",
        ),
        Check(
            "Value can multiply two values",
            value_can_multiply_two_values,
            CORE,
            hint="Implement __mul__ following same pattern as __add__",
        ),
        Check(
            "Multiplication creates proper graph structure",
            multiplication_creates_graph_structure,
            CORE,
        ),
        Check(
            "Backward computes correct gradients for addition",
            backward_computes_gradients_for_addition,
            CORE,
            hint="In _backward for add: both children get gradient 1.0 from parent",
        ),
        Check(
            "Backward computes correct gradients for multiplication",
            backward_computes_gradients_for_multiplication,
            CORE,
            hint="In _backward for mul: child a gets b's value, child b gets a's value",
        ),
        Check(
            "Gradients accumulate when a node appears multiple times",
            backward_accumulates_gradients_on_reused_nodes,
            CORE,
            hint="Using += in _backward allows gradients to accumulate",
        ),
        Check(
            "Backward works through complex graphs with multiple paths",
            backward_works_through_complex_graphs,
            CORE,
            hint="Topological sort ensures nodes are visited in correct order",
        ),
        Check(
            "Value supports multiplication with scalars",
            value_supports_multiplication_with_scalars,
            CORE,
            hint="Convert int/float to Value in __mul__",
        ),
        Check(
            "Reverse multiplication works",
            reverse_multiplication_works,
            CORE,
            hint="Implement __rmul__ to handle scalar * Value",
        ),
        Check(
            "Value supports power operation",
            value_supports_power_operation,
            CORE,
            hint="Implement __pow__ using power rule: d(x^n)/dx = n*x^(n-1)",
        ),
        Check(
            "Backward computes correct gradient for power",
            backward_computes_power_gradient,
            CORE,
        ),
        Check(
            "Value supports negation",
            value_supports_negation,
            CORE,
            hint="Implement __neg__ as multiplication by -1",
        ),
        Check(
            "Value supports subtraction",
            value_supports_subtraction,
            CORE,
            hint="Implement __sub__ as addition with negation",
        ),
        Check(
            "Backward works through subtraction",
            backward_works_through_subtraction,
            CORE,
        ),
        Check(
            "Value supports division",
            value_supports_division,
            CORE,
            hint="Implement __truediv__ as multiplication by power(-1)",
        ),
        Check(
            "repr shows data and gradient",
            repr_shows_data_and_gradient,
            CORE,
            hint="Return string like 'Value(data=5.0, grad=2.0)'",
        ),
        Check(
            "Backward gradients match finite differences",
            backward_gradients_match_finite_differences,
            STRETCH,
            hint="Numerical gradient is (f(x+eps) - f(x-eps)) / (2*eps)",
        ),
        Check(
            "Reverse subtraction works",
            value_supports_reverse_subtraction,
            STRETCH,
            hint="Implement __rsub__",
        ),
        Check(
            "Complex nested expressions work",
            value_supports_complex_nested_expressions,
            STRETCH,
        ),
    ],
)
