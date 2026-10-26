# Python ASE Skill

Expert assistance for working with the [Atomic Simulation Environment (ASE)](https://wiki.fysik.dtu.dk/ase/) Python library.

## What This Skill Does

This skill enhances Claude Code with deep knowledge of ASE, enabling it to help you:

- **Build atomic structures** - Molecules, surfaces, bulk crystals, nanoparticles
- **Set up calculations** - Configure VASP, GPAW, Quantum ESPRESSO, and other calculators
- **Run simulations** - Geometry optimization, molecular dynamics, NEB calculations
- **Analyze results** - Extract energies, forces, trajectories, band structures
- **Write automation scripts** - High-throughput workflows and batch processing
- **Debug issues** - Identify common problems and suggest fixes

## When to Use This Skill

Claude will automatically use this skill when you're working with ASE-related tasks. You can also explicitly request it:

- "Using the python-ase skill, help me set up a Pt(111) surface calculation"
- "Show me how to calculate adsorption energies with ASE"
- "What's the best way to run NEB in ASE?"

## What You Get

### 1. Complete Working Examples

Ask for help and get production-ready code:

```python
# Example: "Help me create a Pt(111) surface with CO adsorbed"
from ase.build import fcc111, add_adsorbate
from ase.optimize import BFGS
from ase.calculators.vasp import Vasp

# Build structure
slab = fcc111('Pt', size=(4, 4, 4), vacuum=10.0)
add_adsorbate(slab, 'CO', height=2.0, position='fcc')

# Set up calculator
calc = Vasp(xc='PBE', encut=400, kpts=(4, 4, 1))
slab.calc = calc

# Optimize
opt = BFGS(slab, trajectory='opt.traj')
opt.run(fmax=0.05)
```

### 2. Best Practices Guidance

- Appropriate convergence criteria for your calculation type
- Common pitfalls and how to avoid them
- Performance optimization tips
- Proper error handling

### 3. Complete Workflows

End-to-end examples for common tasks:
- Surface adsorption energy calculations
- Lattice constant optimization
- Reaction barrier calculations (NEB)
- Band structure and DOS
- Molecular dynamics setup

### 4. Quick Reference

Fast access to common patterns:
- Structure building cheat sheet
- Calculator templates (VASP, GPAW, etc.)
- Optimization setups
- I/O operations
- Convergence testing

## Installation Requirements

To use this skill effectively, you need:

```bash
# Install ASE
pip install ase

# Optional: Install calculators you plan to use
pip install gpaw  # For GPAW
# VASP, Quantum ESPRESSO, etc. require separate installation
```

## Example Interactions

### Example 1: Building a Surface
```
You: Help me create an Au(111) surface with an oxygen atom adsorbed

Claude: I'll help you create an Au(111) surface with oxygen adsorption using ASE.
[Provides complete code with explanations]
```

### Example 2: Running Calculations
```
You: Set up a VASP geometry optimization for this structure

Claude: I'll set up a VASP calculation with appropriate parameters for geometry optimization.
[Provides calculator setup, optimization code, and convergence criteria]
```

### Example 3: Analyzing Results
```
You: How do I extract the adsorption energy from my calculation?

Claude: To calculate the adsorption energy, you need three separate calculations...
[Provides complete workflow with code]
```

### Example 4: Troubleshooting
```
You: My optimization isn't converging, what should I check?

Claude: Let me help you debug the optimization issue. Common problems include...
[Provides debugging steps and validation code]
```

## Skill Contents

- **SKILL.md** - Complete ASE reference for Claude (~350 lines)
  - Core concepts and workflows
  - Common patterns with code examples
  - Best practices and debugging tips

- **QUICK_REFERENCE.md** - Condensed cheat sheet
  - Structure building patterns
  - Calculator templates
  - I/O operations
  - Convergence criteria

- **examples/** - Working example scripts
  - `adsorption_energy.py` - Calculate adsorption energies
  - `lattice_optimization.py` - Optimize lattice constants
  - `neb_barrier.py` - Calculate reaction barriers

## Tips for Best Results

1. **Be specific** about your calculation type (optimization, MD, static, bands)
2. **Mention your calculator** if you have a preference (VASP, GPAW, etc.)
3. **Share error messages** for debugging help
4. **Ask for validation** - Claude can help check structures before expensive calculations

## Skill Level

This skill is suitable for:
- **Beginners** - Clear examples and explanations
- **Intermediate** - Best practices and optimization tips
- **Advanced** - Complex workflows (NEB, band structures, automation)

## Related Skills

- `python-pymatgen` - Materials analysis and structure manipulation
- `python-testing` - Writing tests for your ASE scripts
- `eln` - Documenting computational experiments

## Contributing

If you find issues or have suggestions for improving this skill:
1. Submit an issue to the knowhow repository
2. Suggest additional examples or workflows
3. Share common problems you'd like documented

## License

This skill documentation is part of the knowhow project (MIT License).

## Resources

- [ASE Official Documentation](https://wiki.fysik.dtu.dk/ase/)
- [ASE Tutorial](https://wiki.fysik.dtu.dk/ase/tutorials/tutorials.html)
- [ASE GitHub](https://gitlab.com/ase/ase)
