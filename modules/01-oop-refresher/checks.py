"""Checks for module 01 - OOP refresher.

Read this file. It is the spec. If a check's name and its code disagree, the
code wins, and that is a bug worth an issue.
"""

from __future__ import annotations

import numpy as np

from gym.checks import (
    CORE,
    STRETCH,
    Check,
    CheckSuite,
    assert_close,
    assert_equal,
    assert_shape,
    require,
)


def _relu(m):
    return require(m, "ReLU")()


def _linear(m, in_features=3, out_features=2, seed=0):
    return require(m, "Linear")(in_features, out_features, seed=seed)


# --- core --------------------------------------------------------------------


def layer_is_abstract(m):
    layer_cls = require(m, "Layer")
    try:
        layer_cls()
    except TypeError:
        return
    raise AssertionError(
        "Layer() succeeded, so Layer is not abstract yet - a base class this loose "
        "lets a broken subclass through unnoticed"
    )


def calling_a_layer_runs_forward(m):
    relu = _relu(m)
    x = np.array([[-1.0, 2.0]])
    assert_close(relu(x), relu.forward(x), "relu(x) compared with relu.forward(x)")


def linear_has_the_right_shapes(m):
    layer = _linear(m, 3, 2)
    assert_shape(require(layer, "W"), (3, 2), "Linear.W")
    assert_shape(require(layer, "b"), (2,), "Linear.b")


def linear_starts_with_zero_bias(m):
    layer = _linear(m, 4, 3)
    assert_close(layer.b, np.zeros(3), "Linear.b at initialisation")


def linear_computes_the_affine_map(m):
    layer = _linear(m, 3, 2)
    x = np.array([[1.0, 2.0, 3.0], [-1.0, 0.0, 1.0]])
    assert_close(layer(x), x @ layer.W + layer.b, "Linear output compared with x @ W + b")


def linear_output_shape_follows_the_batch(m):
    layer = _linear(m, 3, 2)
    assert_shape(layer(np.zeros((7, 3))), (7, 2), "Linear output for a batch of 7")


def same_seed_gives_same_weights(m):
    assert_close(
        _linear(m, 5, 4, seed=7).W, _linear(m, 5, 4, seed=7).W, "W for two layers seeded 7"
    )


def different_seeds_give_different_weights(m):
    a, b = _linear(m, 5, 4, seed=1).W, _linear(m, 5, 4, seed=2).W
    if np.allclose(a, b):
        raise AssertionError("seeds 1 and 2 produced identical weights - is the seed being used?")


def relu_zeroes_negatives(m):
    x = np.array([[-2.0, -0.1, 0.0, 0.1, 2.0]])
    assert_close(_relu(m)(x), np.array([[0.0, 0.0, 0.0, 0.1, 2.0]]), "ReLU output")


def relu_does_not_modify_its_input(m):
    x = np.array([[-1.0, 1.0]])
    _relu(m)(x)
    if not np.allclose(x, np.array([[-1.0, 1.0]])):
        raise AssertionError(
            f"the caller's array was [[-1.0, 1.0]] before ReLU and {x.tolist()} after - "
            "ReLU rewrote the array it was handed instead of returning a new one"
        )


def sequential_applies_layers_in_order(m):
    sequential_cls, x = require(m, "Sequential"), np.array([[1.0, -1.0]])
    first, second = _linear(m, 2, 3, seed=0), _linear(m, 3, 2, seed=1)
    model = sequential_cls(first, _relu(m), second)
    assert_close(model(x), second(np.maximum(first(x), 0.0)), "Sequential output")


def sequential_collects_parameters(m):
    first, second = _linear(m, 2, 3, seed=0), _linear(m, 3, 2, seed=1)
    model = require(m, "Sequential")(first, _relu(m), second)
    params = require(model, "parameters")()
    assert_equal(len(params), 4, "the number of parameter arrays in a two-Linear model")


def activations_have_no_parameters(m):
    assert_equal(list(require(_relu(m), "parameters")()), [], "ReLU().parameters()")


def sequential_supports_len_and_indexing(m):
    relu = _relu(m)
    model = require(m, "Sequential")(_linear(m, 2, 3), relu)
    assert_equal(len(model), 2, "len(model)")
    if model[1] is not relu:
        raise AssertionError("model[1] should be the exact ReLU instance that was passed in")


def linear_repr_shows_its_shape(m):
    assert_equal(
        repr(_linear(m, 3, 2)), "Linear(in_features=3, out_features=2)", "repr(Linear(3, 2))"
    )


def activation_repr_is_its_class_name(m):
    assert_equal(repr(_relu(m)), "ReLU()", "repr(ReLU())")


def sequential_repr_lists_its_layers(m):
    model = require(m, "Sequential")(_linear(m, 2, 4), _relu(m), _linear(m, 4, 1))
    expected = (
        "Sequential(Linear(in_features=2, out_features=4), ReLU(), "
        "Linear(in_features=4, out_features=1))"
    )
    assert_equal(repr(model), expected, "repr of a three-layer Sequential")


def num_parameters_counts_every_scalar(m):
    model = require(m, "Sequential")(_linear(m, 2, 4), _relu(m), _linear(m, 4, 1))
    # (2*4 + 4) + (4*1 + 1) = 17
    assert_equal(require(m, "num_parameters")(model), 17, "num_parameters of the model")


# --- stretch -----------------------------------------------------------------


def tanh_matches_numpy(m):
    x = np.array([[-2.0, 0.0, 0.5]])
    assert_close(require(m, "Tanh")()(x), np.tanh(x), "Tanh output")


def layernorm_normalises_the_last_axis(m):
    x = np.array([[1.0, 2.0, 3.0, 4.0], [10.0, 0.0, -5.0, 2.0]])
    out = require(m, "LayerNorm")(4)(x)
    assert_close(out.mean(axis=-1), np.zeros(2), "the per-row mean after LayerNorm", tol=1e-5)
    assert_close(
        out.std(axis=-1), np.ones(2), "the per-row standard deviation after LayerNorm", tol=1e-3
    )


def layernorm_exposes_gamma_and_beta(m):
    layer = require(m, "LayerNorm")(4)
    assert_equal(len(require(layer, "parameters")()), 2, "the number of LayerNorm parameters")
    assert_close(require(layer, "gamma"), np.ones(4), "LayerNorm.gamma at initialisation")
    assert_close(require(layer, "beta"), np.zeros(4), "LayerNorm.beta at initialisation")


def sequential_is_iterable(m):
    layers = [_linear(m, 2, 2), _relu(m)]
    if list(require(m, "Sequential")(*layers)) != layers:
        raise AssertionError("iterating the model did not yield its layers, in order")


SUITE = CheckSuite(
    entrypoint="nn.py",
    checks=[
        Check(
            "Layer cannot be instantiated on its own",
            layer_is_abstract,
            CORE,
            hint="abc.ABC plus @abstractmethod on forward",
        ),
        Check(
            "Calling a layer runs its forward pass",
            calling_a_layer_runs_forward,
            CORE,
            hint="define __call__ once, on the base class",
        ),
        Check("Linear builds W and b with the right shapes", linear_has_the_right_shapes, CORE),
        Check("Linear starts with a zero bias", linear_starts_with_zero_bias, CORE),
        Check("Linear computes x @ W + b", linear_computes_the_affine_map, CORE),
        Check("Linear keeps the batch dimension", linear_output_shape_follows_the_batch, CORE),
        Check(
            "The same seed gives the same weights",
            same_seed_gives_same_weights,
            CORE,
            hint="np.random.default_rng(seed), not np.random.randn",
        ),
        Check(
            "Different seeds give different weights", different_seeds_give_different_weights, CORE
        ),
        Check("ReLU zeroes negative values", relu_zeroes_negatives, CORE),
        Check(
            "ReLU leaves its input unchanged",
            relu_does_not_modify_its_input,
            CORE,
            hint="np.maximum returns a new array; x[x < 0] = 0 edits the caller's array",
        ),
        Check("Sequential applies its layers in order", sequential_applies_layers_in_order, CORE),
        Check(
            "Sequential collects the parameters of every layer", sequential_collects_parameters, CORE
        ),
        Check("A layer with no weights reports no parameters", activations_have_no_parameters, CORE),
        Check(
            "Sequential supports len() and indexing",
            sequential_supports_len_and_indexing,
            CORE,
            hint="__len__ and __getitem__",
        ),
        Check("repr(Linear) shows its shape", linear_repr_shows_its_shape, CORE),
        Check(
            "repr of an activation is its class name",
            activation_repr_is_its_class_name,
            CORE,
            hint="one __repr__ on the base class covers every activation",
        ),
        Check("repr(Sequential) lists the layers it holds", sequential_repr_lists_its_layers, CORE),
        Check("num_parameters counts every weight and bias", num_parameters_counts_every_scalar, CORE),
        Check("Tanh matches np.tanh", tanh_matches_numpy, STRETCH),
        Check("LayerNorm normalises the last axis", layernorm_normalises_the_last_axis, STRETCH),
        Check("LayerNorm exposes gamma and beta", layernorm_exposes_gamma_and_beta, STRETCH),
        Check("Iterating a Sequential yields its layers", sequential_is_iterable, STRETCH, hint="__iter__"),
    ],
)
