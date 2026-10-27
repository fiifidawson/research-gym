# 02 · Autograd from scratch

**Submit:** `submissions/<your-handle>/02-autograd/autograd.py`  
**Starter:** [`starter/autograd.py`](starter/autograd.py)  
**Checks:** [`checks.py`](checks.py)

## What you're building

A `Value` class that wraps a scalar and tracks how it was computed. An implementation of the backward pass using topological sort and the chain rule.

No external autograd library. You're building the thing that PyTorch's `autograd` does under the hood.

## Why

The chain rule is a formula until you write the code that applies it. Then it becomes intuition.

Once you've built autograd, reading PyTorch's autograd behavior goes from "magic" to "oh, that's how they organized it."

Understanding backpropagation deeply is how you debug training, design new architectures, and read research papers with confidence.

## Read first

- [The spelled-out intro to neural networks and backpropagation](https://www.youtube.com/watch?v=VMj-3S1tku0) -
  this module is that video, done yourself. Watch it once before you start.
- [The chain rule](https://en.wikipedia.org/wiki/Chain_rule) - the one piece of calculus this
  module is built on.
- [Python data model](https://docs.python.org/3/reference/datamodel.html#special-method-names) -
  `__add__`, `__mul__`, `__radd__`, `__rmul__`.
- [Emulating numeric types](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types) -
  which method Python calls for which operator, and when it falls back to the reverse one.
- [How the backpropagation algorithm works](http://neuralnetworksanddeeplearning.com/chap2.html) -
  chapter 2, for the version with the maths written out.

## Core

Copy `starter/autograd.py` into your folder and work through the TODOs. Keep the names exactly as given - the checks look them up by name, and module 03 imports this file.

1. **`Value.__init__`** - Store data, children, operation, and initialize gradient to 0. Also initialize `_backward` to a no-op lambda.

2. **`__add__` and `__radd__`** - Create a new Value for a + b. Store both values as children and 'add' as the operation. Define `_backward()` to apply the chain rule for addition (both gradients get the full upstream gradient).

3. **`__mul__` and `__rmul__`** - Same pattern as add, but the local derivatives are different. For c = a * b, the gradient flowing to a is multiplied by b, and vice versa.

4. **`__neg__`** - Negate a value. Implement as multiplication by -1.

5. **`__sub__`** - Subtraction. Implement as a + (-b). `__rsub__`, which is what makes
   `5 - Value(3)` work, is a stretch item.

6. **`__truediv__`** - Division. Implement as a * (b ** -1).

7. **`__pow__`** - Power (exponent must be a constant number, not a Value). Use the power rule: d(a^n)/da = n * a^(n-1).

8. **`__repr__`** - String representation showing data and gradient.

9. **`backward()`** - The core algorithm. Topological sort to visit nodes in reverse order of creation, then walk backward calling `_backward()` on each node.

The key insight: each operation stores a `_backward` function that knows how to propagate gradients one step backward using the chain rule. Backward() just calls them in the right order.

## Stretch

Optional, doesn't block a merge.

- **`__rsub__`** - so `5 - Value(3)` works, not just `Value(5) - Value(3)`.
- Check your gradients against finite differences. Nudge a value by a tiny amount, see how much
  the output moved, and compare that with the gradient you computed.
- Hold up under a nested expression - something like `(a + b) * (a - b)`, where one value reaches
  the output along more than one path.

Not checked, but worth doing if you have the appetite: more operations (`exp`, `log`, `tanh`), and
timing the backward pass on a large graph.

## Checking it

Open the pull request. The check comments with every item above, passed or failed. Push again and
the comment updates. 18 core checks; when they're all green, ask for a review.

For instant feedback, the Playground page on the site runs the same `checks.py` in your browser.

**Done:** 18/18 core, one approval, merged.

## Next

Module 03 imports this file and builds a training loop using it. Your Value class will be the foundation for everything that follows.
