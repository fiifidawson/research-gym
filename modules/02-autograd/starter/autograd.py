"""Module 02 - Autograd from scratch.

Copy this to `submissions/<your-handle>/02-autograd/autograd.py` and fill in the
TODOs there. Leave this starter alone so the next person gets a clean copy.

Keep every class, method, and attribute name as written. The checks look them
up by name, and module 03 imports this file.
"""

from __future__ import annotations


class Value:
    """A scalar that tracks its computation graph.

    When you perform operations (add, multiply, etc.), a Value remembers:
    - What data it holds
    - How it was computed (which operation)
    - Which Values created it (its children)

    This lets backward() walk backward through the graph and apply the chain rule.
    """

    def __init__(
        self,
        data: float,
        _children: tuple[Value, ...] = (),
        _op: str = "",
    ) -> None:
        """Initialize a Value.

        Args:
            data: The scalar number (int or float)
            _children: Tuple of Values that created this one (for the graph)
            _op: String name of operation that created this ("add", "mul", etc)

        TODO: Store all three arguments as instance attributes.
        TODO: Initialize `self.grad = 0.0`. Gradients accumulate here during backward().
        TODO: Initialize `self._backward = lambda: None`. This will be overwritten
              for non-leaf nodes (see __add__, __mul__, etc). Leaf nodes keep
              the no-op so backward() doesn't crash.
        """
        raise NotImplementedError

    def __add__(self, other: Value | float) -> Value:
        """Addition: a + b creates a new Value that remembers 'a' and 'b' and 'add'.

        TODO: Convert `other` to a Value if it's a number (int or float).

        TODO: Create a new Value for the output.
              - data: self.data + other.data
              - _children: tuple containing both self and other
              - _op: the string 'add'

        TODO: Define a local function `_backward()`. It runs later, during
              backward(), and its job is to take the output's gradient
              (`out.grad`) and push it on to each child.

              Work out d(a+b)/da and d(a+b)/db yourself. They are the easiest
              two derivatives in this file, and deriving them rather than
              copying them is the whole point of the module.

              Accumulate with `+=`, never assign with `=`. A value used twice
              in one expression earns a gradient along each path, and `=`
              throws the first one away.

        TODO: Attach _backward to the output so it will be called during backward().

        TODO: Return the output Value.
        """
        raise NotImplementedError

    def __radd__(self, other: Value | float) -> Value:
        """Reverse add: lets 5 + Value(3) work (calls Value(3).__radd__(5))."""
        # TODO: Use __add__ to handle it (addition is commutative)
        raise NotImplementedError

    def __mul__(self, other: Value | float) -> Value:
        """Multiplication: a * b creates a new Value that remembers the operation.

        TODO: Convert `other` to a Value if it's a number.

        TODO: Create a new Value for the output.
              - data: self.data * other.data
              - _children: tuple containing both self and other
              - _op: the string 'mul'

        TODO: Define _backward() for multiplication. Same shape as add, but
              the local derivatives are not 1 any more: differentiate a * b
              with respect to a, then with respect to b.

              If you get stuck, the Karpathy video in Read first derives this
              one on screen.

        TODO: Attach _backward to output and return it.
        """
        raise NotImplementedError

    def __rmul__(self, other: Value | float) -> Value:
        """Reverse multiply: lets 5 * Value(3) work."""
        # TODO: Use __mul__ (multiplication is commutative)
        raise NotImplementedError

    def __neg__(self) -> Value:
        """Negation: -a is implemented as a * -1."""
        # TODO: Use multiplication by -1
        raise NotImplementedError

    def __sub__(self, other: Value | float) -> Value:
        """Subtraction: a - b is a + (-b)."""
        # TODO: Implement using addition and negation
        raise NotImplementedError

    def __rsub__(self, other: Value | float) -> Value:
        """Reverse subtraction: lets 5 - Value(3) work."""
        # TODO (stretch): Use subtraction
        raise NotImplementedError

    def __truediv__(self, other: Value | float) -> Value:
        """Division: a / b is a * (b ** -1)."""
        # TODO: Implement using multiplication and power
        raise NotImplementedError

    def __pow__(self, other: float) -> Value:
        """Power: a ** n where n is a number.

        TODO: Assert that `other` is int or float (exponent must be constant).

        TODO: Create a new Value for the output.
              - data: self.data ** other
              - _children: tuple containing just self
              - _op: the string f'**{other}' (e.g., '**2')

        TODO: Define _backward(). The exponent is held constant, which is what
              makes this the power rule from school calculus: differentiate
              a ** n with respect to a.

              Only one child here, so only one gradient to push back.

        TODO: Attach _backward and return output.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """String representation for debugging."""
        # TODO: Return a string showing data and grad, e.g.:
        # "Value(data=5.0, grad=1.0)"
        raise NotImplementedError

    def backward(self) -> None:
        """Backward pass: walk the computation graph and apply the chain rule.

        This is the core of automatic differentiation. The idea:
        1. Start with the output node (self), which has gradient 1.0
        2. Walk backward through the graph in reverse topological order
        3. For each node, call its _backward() to propagate gradients to children
        4. Each _backward() uses the chain rule: child.grad += parent.grad * local_derivative

        Reverse topological order matters: visit nodes only after visiting all
        nodes that depend on them. This ensures gradients accumulate correctly.

        TODO: Build a list `topo` of nodes in reverse topological order.
              - Keep a `visited` set to avoid processing nodes twice
              - Use depth-first search (recursion) starting from self
              - Add a node to `topo` AFTER visiting all its children

        TODO: Set self.grad = 1.0 (gradient of output w.r.t. itself is 1)

        TODO: Walk through `topo` in reverse order (so earliest nodes are last).
              For each node v, call v._backward(). This propagates gradients
              one step backward in the chain rule.
        """
        raise NotImplementedError
