---
name: python-jax
description: Expert guidance for JAX (Just After eXecution) - high-performance numerical computing with automatic differentiation, JIT compilation, vectorization, and GPU/TPU acceleration; includes transformations (grad, jit, vmap, pmap), sharp bits, gotchas, and differences from NumPy
allowed-tools: ["*"]
---

# JAX - High-Performance Numerical Computing

## Overview

**JAX** is a Python library for accelerator-oriented array computation and program transformation, designed for high-performance numerical computing and large-scale machine learning. It combines a familiar NumPy-style API with powerful function transformations for automatic differentiation, compilation, vectorization, and parallelization.

**Core value:** Write NumPy-like Python code and automatically get gradients, GPU/TPU acceleration, vectorization, and parallelization through composable function transformations—without changing your mathematical notation.

## When to Use JAX

**Use JAX when:**
- Need automatic differentiation for optimization or machine learning
- Want GPU/TPU acceleration with minimal code changes
- Require high-performance numerical computing
- Building custom gradient-based algorithms
- Need to vectorize or parallelize functions automatically
- Working on research requiring flexible differentiation
- Want functional programming approach to numerical code

**Don't use when:**
- Simple NumPy operations without performance needs (overhead not justified)
- Heavy reliance on in-place mutations (JAX arrays are immutable)
- Imperative, stateful code with side effects
- Need control flow depending on runtime data values (limited support)
- Working with libraries that require NumPy arrays (compatibility issues)

## Core Transformations

JAX provides four fundamental, composable transformations:

### 1. `jax.grad` - Automatic Differentiation

Compute gradients automatically using reverse-mode autodiff.

```python
import jax
import jax.numpy as jnp

def loss(x):
    return jnp.sum(x**2)

# Get gradient function
grad_loss = jax.grad(loss)

x = jnp.array([1.0, 2.0, 3.0])
gradient = grad_loss(x)
print(gradient)  # [2. 4. 6.]
```

**Key features:**
- Returns a function that computes gradients
- Composes for higher-order derivatives
- Works with complex nested structures (pytrees)

### 2. `jax.jit` - Just-In-Time Compilation

Compile functions to XLA for dramatic speedups.

```python
import jax

@jax.jit
def fast_function(x):
    return jnp.sum(x**2 + 3*x + 1)

# First call: compilation + execution (slower)
result = fast_function(jnp.array([1.0, 2.0, 3.0]))

# Subsequent calls: cached compiled version (much faster)
result = fast_function(jnp.array([4.0, 5.0, 6.0]))
```

**Performance:**
- 10-100x speedup typical for numerical functions
- First call slower (compilation overhead)
- Cached for subsequent calls with same shapes/dtypes

### 3. `jax.vmap` - Automatic Vectorization

Vectorize functions across batch dimensions automatically.

```python
import jax

def process_single(x):
    """Process single example"""
    return jnp.sum(x**2)

# Vectorize to process batch
process_batch = jax.vmap(process_single)

# Works on batch automatically
batch = jnp.array([[1, 2], [3, 4], [5, 6]])
results = process_batch(batch)
print(results)  # [5 25 61]
```

**Benefits:**
- Eliminates manual loop writing
- Often faster than explicit loops
- Cleaner, more declarative code

### 4. `jax.pmap` - Parallel Map

Parallelize across multiple devices (GPUs/TPUs).

```python
import jax

@jax.pmap
def parallel_fn(x):
    return x**2

# Runs on all available devices
devices = jax.devices()
x = jnp.arange(len(devices))
results = parallel_fn(x)
```

**Use for:**
- Multi-GPU/TPU computation
- Data parallelism in training
- Large-scale simulations

## Transformation Composition

**JAX transformations compose seamlessly:**

```python
# Gradient of JIT-compiled function
@jax.jit
def fast_loss(x):
    return jnp.sum(x**2)

grad_fast_loss = jax.grad(fast_loss)

# JIT of gradient (equally valid)
fast_grad_loss = jax.jit(jax.grad(fast_loss))

# Vectorized gradient
batch_grad_loss = jax.vmap(jax.grad(fast_loss))

# JIT + vmap + grad
fast_batch_grad = jax.jit(jax.vmap(jax.grad(fast_loss)))
```

**Order matters for performance but not correctness.**

## JAX vs NumPy - Critical Differences

### 1. Immutability

**NumPy (mutable):**
```python
import numpy as np
x = np.array([1, 2, 3])
x[0] = 10  # Modifies x in-place
print(x)  # [10 2 3]
```

**JAX (immutable):**
```python
import jax.numpy as jnp
x = jnp.array([1, 2, 3])
# x[0] = 10  # ERROR: JAX arrays are immutable

# Use functional update instead
x = x.at[0].set(10)  # Returns NEW array
print(x)  # [10 2 3]
```

**Functional updates:**
```python
# Set value
x = x.at[0].set(10)

# Add to value
x = x.at[0].add(5)

# Multiply value
x = x.at[0].mul(2)

# Min/max
x = x.at[0].min(5)
x = x.at[0].max(5)

# Multi-index
x = x.at[0, 1].set(10)
x = x.at[[0, 2]].set(10)
x = x.at[0:3].set(10)
```

### 2. Random Number Generation

**NumPy (global state):**
```python
import numpy as np
np.random.seed(42)
x = np.random.normal(size=3)
y = np.random.normal(size=3)  # Different from x
```

**JAX (explicit keys):**
```python
import jax
key = jax.random.PRNGKey(42)

# Split key for independent randomness
key, subkey = jax.random.split(key)
x = jax.random.normal(subkey, shape=(3,))

key, subkey = jax.random.split(key)
y = jax.random.normal(subkey, shape=(3,))

# Parallel random numbers
keys = jax.random.split(key, num=10)
samples = jax.vmap(lambda k: jax.random.normal(k, shape=(3,)))(keys)
```

**Key management pattern:**
```python
# Create initial key
key = jax.random.PRNGKey(0)

# Always split before using
key, subkey1, subkey2 = jax.random.split(key, 3)

# Use subkeys for random operations
x = jax.random.normal(subkey1, shape=(10,))
y = jax.random.uniform(subkey2, shape=(10,))

# Never reuse keys!
```

### 3. 64-bit Precision

**JAX defaults to 32-bit** for performance.

```python
import jax.numpy as jnp

x = jnp.array([1.0])
print(x.dtype)  # float32 (default)

# Enable 64-bit globally
from jax import config
config.update("jax_enable_x64", True)

x = jnp.array([1.0])
print(x.dtype)  # float64

# Or use environment variable
# JAX_ENABLE_X64=1 python script.py
```

### 4. Out-of-Bounds Indexing

**NumPy (raises error):**
```python
import numpy as np
x = np.array([1, 2, 3])
# x[10]  # IndexError
```

**JAX (clamps silently):**
```python
import jax.numpy as jnp
x = jnp.array([1, 2, 3])
print(x[10])  # 3 (returns last element, no error!)

# Updates also silently ignored
x = x.at[10].set(99)  # No error, no effect
```

**⚠️ Warning:** This is **undefined behavior** - avoid relying on it!

### 5. Non-Array Inputs

**NumPy (accepts lists):**
```python
import numpy as np
result = np.sum([1, 2, 3])  # Works
```

**JAX (requires arrays):**
```python
import jax.numpy as jnp
# result = jnp.sum([1, 2, 3])  # ERROR

# Convert explicitly
result = jnp.sum(jnp.array([1, 2, 3]))  # Works
```

**Reason:** Prevents performance degradation during tracing.

## Sharp Bits & Gotchas

### 1. Pure Functions Required

**❌ Bad: Side effects**
```python
counter = 0

@jax.jit
def impure_fn(x):
    global counter
    counter += 1  # Side effect - UNRELIABLE
    return x**2

# First call: counter=1 (traced)
result = impure_fn(2.0)
# Subsequent calls: counter STILL 1 (uses cached trace)
result = impure_fn(3.0)
```

**✅ Good: Pure function**
```python
@jax.jit
def pure_fn(x, counter):
    return x**2, counter + 1

result, counter = pure_fn(2.0, 0)
result, counter = pure_fn(3.0, counter)
```

### 2. Control Flow Limitations

**❌ Bad: Value-dependent control flow**
```python
@jax.jit
def conditional(x):
    if x > 0:  # ERROR: x is tracer, not concrete value
        return x**2
    else:
        return x**3
```

**✅ Good: Use jax.lax.cond**
```python
@jax.jit
def conditional(x):
    return jax.lax.cond(
        x > 0,
        lambda x: x**2,  # True branch
        lambda x: x**3   # False branch
    )
```

**For loops:**
```python
# ❌ Bad: Python for loop in JIT (unrolled at compile time)
@jax.jit
def loop_bad(x, n):
    for i in range(n):  # n must be static
        x = x + 1
    return x

# ✅ Good: Use jax.lax.fori_loop
@jax.jit
def loop_good(x, n):
    def body(i, val):
        return val + 1
    return jax.lax.fori_loop(0, n, body, x)
```

**While loops:**
```python
@jax.jit
def while_loop(x):
    def cond_fun(val):
        return val < 10

    def body_fun(val):
        return val + 1

    return jax.lax.while_loop(cond_fun, body_fun, x)
```

### 3. Dynamic Shapes

**❌ Bad: Shape depends on runtime values**
```python
@jax.jit
def dynamic_shape(x, mask):
    return x[mask]  # ERROR: output shape unknown at compile time
```

**✅ Good: Use jnp.where for masking**
```python
@jax.jit
def static_shape(x, mask):
    return jnp.where(mask, x, 0)  # Shape stays same
```

### 4. In-Place Update Semantics

**❌ Bad: Relying on shared references**
```python
x = jnp.array([1, 2, 3])
y = x
x = x.at[0].set(10)
print(y[0])  # Still 1 (y unchanged)
```

**Note:** `.at` returns a NEW array; doesn't modify original.

### 5. Print Debugging in JIT

**❌ Bad: print() in JIT context**
```python
@jax.jit
def debug(x):
    print(f"x = {x}")  # Only prints ONCE (during trace)
    return x**2
```

**✅ Good: Use jax.debug.print**
```python
@jax.jit
def debug(x):
    jax.debug.print("x = {}", x)  # Prints every call
    return x**2
```

### 6. Gradient Through Discrete Operations

**❌ Bad: Gradient through argmax**
```python
def loss(x):
    idx = jnp.argmax(x)  # Discrete - no gradient
    return x[idx]

# grad_loss = jax.grad(loss)  # Gradient is zero everywhere
```

**✅ Good: Use differentiable approximations**
```python
def loss(x):
    # Soft argmax (differentiable)
    weights = jax.nn.softmax(x * temperature)
    return jnp.sum(x * weights)

grad_loss = jax.grad(loss)
```

## Automatic Differentiation

### Basic Gradient

```python
import jax
import jax.numpy as jnp

def f(x):
    return jnp.sum(x**2)

grad_f = jax.grad(f)

x = jnp.array([1.0, 2.0, 3.0])
print(grad_f(x))  # [2. 4. 6.]
```

### Value and Gradient

```python
# Compute both value and gradient efficiently
value_and_grad_f = jax.value_and_grad(f)

value, gradient = value_and_grad_f(x)
print(f"Value: {value}, Gradient: {gradient}")
```

### Multiple Arguments

```python
def f(x, y):
    return jnp.sum(x**2 + y**3)

# Gradient w.r.t. first argument (default)
grad_f = jax.grad(f)
print(grad_f(x, y))

# Gradient w.r.t. second argument
grad_f_wrt_y = jax.grad(f, argnums=1)
print(grad_f_wrt_y(x, y))

# Gradients w.r.t. both arguments
grad_f_both = jax.grad(f, argnums=(0, 1))
grad_x, grad_y = grad_f_both(x, y)
```

### Auxiliary Data

```python
def loss_with_aux(x):
    loss = jnp.sum(x**2)
    aux_data = {'norm': jnp.linalg.norm(x), 'mean': jnp.mean(x)}
    return loss, aux_data

# Tell JAX about auxiliary output
grad_fn = jax.grad(loss_with_aux, has_aux=True)
gradient, aux = grad_fn(x)

print(f"Gradient: {gradient}")
print(f"Auxiliary: {aux}")
```

### Higher-Order Derivatives

```python
# Second derivative (Hessian diagonal)
def f(x):
    return jnp.sum(x**3)

grad_f = jax.grad(f)
hess_diag_f = jax.grad(lambda x: jnp.sum(grad_f(x) * x))

# Full Hessian
hessian_f = jax.hessian(f)

x = jnp.array([1.0, 2.0, 3.0])
print(hessian_f(x))
```

### Jacobian

```python
def vector_fn(x):
    """Vector to vector function"""
    return jnp.array([x[0]**2, x[1]**3, x[0]*x[1]])

# Forward-mode (efficient for few inputs, many outputs)
jacfwd = jax.jacfwd(vector_fn)

# Reverse-mode (efficient for many inputs, few outputs)
jacrev = jax.jacrev(vector_fn)

x = jnp.array([2.0, 3.0])
print(jacfwd(x))
print(jacrev(x))  # Same result
```

### Custom Gradients

Use `@jax.custom_vjp` (reverse-mode) or `@jax.custom_jvp` (forward-mode):

```python
@jax.custom_vjp
def f(x):
    return jnp.exp(x)

def f_fwd(x):
    result = jnp.exp(x)
    return result, result  # (output, residuals for backward)

def f_bwd(result, g):
    return (g * 2 * result,)  # Custom: 2x the normal gradient

f.defvjp(f_fwd, f_bwd)

grad_f = jax.grad(f)
```

## JIT Compilation

### Basic Usage

```python
import jax
import jax.numpy as jnp

def slow_fn(x):
    return jnp.sum(x**2 + 3*x + 1)

fast_fn = jax.jit(slow_fn)

# Or decorator
@jax.jit
def fast_fn2(x):
    return jnp.sum(x**2 + 3*x + 1)
```

### Static Arguments

```python
@jax.jit
def fn(x, n):
    for i in range(n):  # n must be static
        x = x + 1
    return x

# ERROR: n changes each call, triggers recompilation
result = fn(x, 5)
result = fn(x, 10)  # Recompiles!

# Solution: Mark as static
@jax.jit(static_argnums=(1,))
def fn_static(x, n):
    for i in range(n):
        x = x + 1
    return x

# Now works correctly
result = fn_static(x, 5)
result = fn_static(x, 10)  # Separate compilation for n=10
```

### Avoiding Recompilation

```python
# Bad: Different shapes trigger recompilation
@jax.jit
def process(x):
    return jnp.sum(x**2)

x1 = jnp.ones(10)    # Compiles for shape (10,)
x2 = jnp.ones(20)    # Recompiles for shape (20,)
x3 = jnp.ones(10)    # Uses cached version

# Good: Consistent shapes
batch_size = 32
x1 = jnp.ones((batch_size, 10))
x2 = jnp.ones((batch_size, 10))  # Same shape, cached
```

## Vectorization (vmap)

### Basic Batching

```python
def process_single(x):
    """Process single example: scalar input"""
    return x**2 + 3*x

# Manually vectorize
def process_batch_manual(xs):
    return jnp.array([process_single(x) for x in xs])

# Automatic vectorization
process_batch = jax.vmap(process_single)

batch = jnp.array([1.0, 2.0, 3.0, 4.0])
print(process_batch(batch))  # Faster and cleaner
```

### Batching Matrix Operations

```python
def matrix_vector_product(matrix, vector):
    """Single matrix-vector product"""
    return matrix @ vector

# Batch over vectors
batch_mvp = jax.vmap(matrix_vector_product, in_axes=(None, 0))

A = jnp.ones((3, 3))
vectors = jnp.ones((10, 3))  # 10 vectors

results = batch_mvp(A, vectors)  # (10, 3)

# Batch over both
batch_both = jax.vmap(matrix_vector_product, in_axes=(0, 0))

matrices = jnp.ones((10, 3, 3))
results = batch_both(matrices, vectors)
```

### Nested vmap

```python
# Batch over two dimensions
def fn(x, y):
    return x * y

# Batch over first arg, then second
fn_batch = jax.vmap(jax.vmap(fn, in_axes=(None, 0)), in_axes=(0, None))

x = jnp.array([1, 2, 3])       # (3,)
y = jnp.array([10, 20])        # (2,)
result = fn_batch(x, y)        # (3, 2)

# Equivalent to: x[:, None] * y[None, :]
```

## PyTrees - Nested Structures

JAX works with nested Python containers (pytrees):

```python
import jax
import jax.numpy as jnp

# Dictionary of arrays
params = {
    'w1': jnp.ones((10, 5)),
    'b1': jnp.zeros(5),
    'w2': jnp.ones((5, 1)),
    'b2': jnp.zeros(1)
}

# Gradient works on entire pytree
def loss(params, x):
    h = x @ params['w1'] + params['b1']
    h = jax.nn.relu(h)
    out = h @ params['w2'] + params['b2']
    return jnp.mean(out**2)

grad_fn = jax.grad(loss)
x = jnp.ones((32, 10))

# Returns gradients in same structure
grads = grad_fn(params, x)
print(grads.keys())  # dict_keys(['w1', 'b1', 'w2', 'b2'])
```

### PyTree Operations

```python
# Tree map - apply function to all leaves (JAX 0.4.25+: use jax.tree.map)
scaled_params = jax.tree.map(lambda x: x * 0.9, params)

# Tree reduce (JAX 0.4.25+: use jax.tree.reduce)
total_params = jax.tree.reduce(
    lambda total, x: total + x.size,
    params,
    initializer=0
)

# Flatten and unflatten
flat, treedef = jax.tree_flatten(params)
reconstructed = jax.tree_unflatten(treedef, flat)
```

## Common Patterns

### Optimization Loop

```python
import jax
import jax.numpy as jnp

# Parameters
params = jnp.array([1.0, 2.0, 3.0])

# Loss function
def loss(params, x, y):
    pred = jnp.dot(params, x)
    return jnp.mean((pred - y)**2)

# Gradient function
grad_fn = jax.jit(jax.grad(loss))

# Training data
x_train = jnp.ones((100, 3))
y_train = jnp.ones(100)

# Optimization loop
learning_rate = 0.01
for step in range(1000):
    grads = grad_fn(params, x_train, y_train)
    params = params - learning_rate * grads

    if step % 100 == 0:
        l = loss(params, x_train, y_train)
        print(f"Step {step}, Loss: {l:.4f}")
```

### Mini-batch Training

```python
def train_step(params, batch):
    """Single training step on one batch"""
    x, y = batch

    def batch_loss(params):
        pred = jnp.dot(x, params)
        return jnp.mean((pred - y)**2)

    loss_value, grads = jax.value_and_grad(batch_loss)(params)
    params = params - 0.01 * grads
    return params, loss_value

# JIT compile training step
train_step = jax.jit(train_step)

# Training loop
for epoch in range(10):
    for batch in data_loader:
        params, loss = train_step(params, batch)
```

### Scan for Efficient Loops

```python
def cumulative_sum(xs):
    """Efficient cumulative sum using scan"""
    def step(carry, x):
        new_carry = carry + x
        output = new_carry
        return new_carry, output

    final_carry, outputs = jax.lax.scan(step, 0, xs)
    return outputs

xs = jnp.array([1, 2, 3, 4, 5])
print(cumulative_sum(xs))  # [1 3 6 10 15]
```

### RNN with Scan

```python
def rnn_step(carry, x):
    """Single RNN step"""
    h = carry
    h_new = jnp.tanh(jnp.dot(W_h, h) + jnp.dot(W_x, x))
    return h_new, h_new

def rnn(xs, h0):
    """Run RNN over sequence"""
    final_h, all_h = jax.lax.scan(rnn_step, h0, xs)
    return all_h

# Process sequence
W_h = jnp.ones((5, 5))
W_x = jnp.ones((5, 3))
xs = jnp.ones((10, 3))  # Sequence length 10
h0 = jnp.zeros(5)

outputs = rnn(xs, h0)  # (10, 5)
```

## Performance Best Practices

### 1. JIT Your Critical Paths

```python
# Wrap expensive computations in jit
@jax.jit
def expensive_fn(x):
    for _ in range(100):
        x = jnp.dot(x, x.T)
    return x

# Avoid jitting trivial operations
def trivial(x):
    return x + 1  # JIT overhead not worth it
```

### 2. Use vmap Instead of Loops

```python
# Slow: Python loop
def slow_batch(xs):
    return jnp.array([process(x) for x in xs])

# Fast: vmap
fast_batch = jax.vmap(process)
```

### 3. Minimize Host-Device Transfers

```python
# Bad: Transfer back to host in loop
for i in range(1000):
    x = compute_on_gpu(x)
    print(float(x))  # Transfers to CPU each iteration!

# Good: Transfer once at end
for i in range(1000):
    x = compute_on_gpu(x)
print(float(x))  # Single transfer
```

### 4. Use Appropriate Precision

```python
# Use float32 unless you need float64
x = jnp.array([1.0, 2.0, 3.0], dtype=jnp.float32)

# Enable float64 only when necessary
from jax import config
config.update("jax_enable_x64", True)
```

### 5. Preallocate When Possible

```python
# Bad: Growing arrays
result = jnp.array([])
for i in range(1000):
    result = jnp.append(result, compute(i))

# Good: Preallocate
result = jnp.zeros(1000)
for i in range(1000):
    result = result.at[i].set(compute(i))

# Better: Use scan or vmap
def compute_all(i):
    return compute(i)

result = jax.vmap(compute_all)(jnp.arange(1000))
```

## Debugging

### Checking Array Values

```python
# Use jax.debug.print in JIT context
@jax.jit
def debug_fn(x):
    jax.debug.print("x = {}", x)
    jax.debug.print("x shape = {}, dtype = {}", x.shape, x.dtype)
    return x**2
```

### Gradient Checking

```python
from jax.test_util import check_grads

def f(x):
    return jnp.sum(x**3)

x = jnp.array([1.0, 2.0, 3.0])

# Verify gradients numerically
check_grads(f, (x,), order=2)  # Check 1st and 2nd derivatives
```

### Inspecting Compiled Code

```python
# See jaxpr (intermediate representation)
def f(x):
    return x**2 + 3*x

jaxpr = jax.make_jaxpr(f)(1.0)
print(jaxpr)

# See HLO (low-level compiled code)
compiled = jax.jit(f).lower(1.0).compile()
print(compiled.as_text())
```

## Common Gotchas - Quick Reference

| Gotcha | NumPy | JAX | Solution |
|--------|-------|-----|----------|
| In-place update | `x[0] = 1` | ❌ Error | `x = x.at[0].set(1)` |
| Random state | `np.random.seed()` | ❌ Not reliable | `key = jax.random.PRNGKey()` |
| List inputs | `np.sum([1,2,3])` | ❌ Error | `jnp.sum(jnp.array([1,2,3]))` |
| Out-of-bounds | IndexError | ⚠️ Silent clamp | Avoid, validate indices |
| Value-dependent if | Works | ❌ In JIT | `jax.lax.cond()` |
| Dynamic shapes | Works | ❌ In JIT | Keep shapes static |
| Default precision | float64 | float32 | Set `jax_enable_x64` |
| Print in JIT | Works | Only once | `jax.debug.print()` |

## Installation

```bash
# CPU only
pip install jax

# GPU (CUDA 12)
pip install jax[cuda12]

# TPU
pip install jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
```

## Ecosystem Libraries

JAX has a rich ecosystem built on its transformation primitives:

**Neural Networks:**
- **Flax** - Official neural network library
- **Haiku** - DeepMind's neural network library (DEPRECATED: migrate to Flax/NNX)
- **Equinox** - Elegant PyTorch-like library

**Optimization:**
- **Optax** - Gradient processing and optimization
- **JAXopt** - Non-linear optimization

**Scientific Computing:**
- **JAX-MD** - Molecular dynamics
- **Diffrax** - Differential equation solvers
- **BlackJAX** - MCMC sampling

**Utilities:**
- **jaxtyping** - Type annotations for arrays
- **chex** - Testing utilities

## Additional Resources

- **Official Documentation:** https://docs.jax.dev/
- **JAX GitHub:** https://github.com/google/jax
- **JAX Ecosystem:** https://github.com/google/jax#neural-network-libraries
- **JAX Tutorial (DeepMind):** https://github.com/deepmind/jax-tutorial
- **Awesome JAX:** https://github.com/n2cholas/awesome-jax

## Related Skills

- `python-optimization` - Numerical optimization with scipy, pyomo
- `python-ase` - Atomic simulation environment (can use JAX for forces)
- `pycse` - Scientific computing utilities
- `python-best-practices` - Code quality for JAX projects
