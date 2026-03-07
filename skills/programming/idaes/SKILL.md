---
name: idaes
description: |
  Comprehensive guidance for using IDAES (Institute for the Design of Advanced Energy Systems)
  for process systems engineering. Covers flowsheet modeling, property packages, unit models,
  optimization, scaling, initialization, and diagnostics. Use when working with chemical process
  simulations, energy systems modeling, power plant design, material and energy balances, or
  process optimization. Triggers include 'IDAES', 'flowsheet', 'process model', 'unit operation',
  'process optimization', 'property package', 'energy systems', or process engineering tasks.
allowed-tools: ["*"]
---

# IDAES Process Systems Engineering

Systematic guidance for using IDAES to model, simulate, and optimize chemical processes and energy systems.

## IDAES Workflow

### 1. Identify Task Type

**What do you want to do?**

**Getting Started:**
- Install and setup → `references/installation.md`
- Understand core concepts → `references/core-concepts.md`
- First flowsheet → `examples/simple_flowsheet.py`

**Flowsheet Development:**
- Build basic flowsheet → `references/flowsheets.md`
- Add unit models → `references/unit-models.md`
- Connect streams → `references/flowsheets.md`
- Set up material/energy balances → `references/flowsheets.md`
- Add time-dependent behavior → `references/dynamic-modeling.md`

**Property Modeling:**
- Select property package → `references/property-packages.md`
- Configure components and phases → `references/property-packages.md`
- Define thermodynamic methods → `references/property-packages.md`
- Add reaction packages → `references/property-packages.md`
- Create custom properties → `references/custom-models.md`

**Unit Operations:**
- Use generic models (mixers, splitters, heaters) → `references/generic-models.md`
- Model power generation equipment → `references/power-generation.md`
- Set up gas-solid contactors → `references/gas-solid-models.md`
- Configure separations → `references/generic-models.md`
- Add reactors → `references/generic-models.md`

**Solving and Optimization:**
- Initialize models → `references/initialization.md`
- Solve flowsheets → `references/solving.md`
- Run optimization → `references/optimization.md`
- Perform parameter estimation → `references/parameter-estimation.md`
- Data reconciliation → `references/parameter-estimation.md`

**Diagnostics and Scaling:**
- Diagnose model issues → `references/diagnostics.md`
- Apply scaling → `references/scaling.md`
- Identify structural problems → `references/diagnostics.md`
- Fix convergence issues → `references/solving.md`

**Analysis:**
- Calculate process economics → `references/costing.md`
- Perform sensitivity analysis → `references/optimization.md`
- Analyze results → `examples/analysis.py`
- Generate reports → `examples/reporting.py`

### 2. Core IDAES Workflow

**Basic pattern:**
```python
# 1. Import IDAES modules
from pyomo.environ import ConcreteModel
from idaes.core import FlowsheetBlock
from idaes.models.properties import iapws95
from idaes.models.unit_models import Heater

# 2. Create model and flowsheet
m = ConcreteModel()
m.fs = FlowsheetBlock(dynamic=False)

# 3. Add property package
m.fs.properties = iapws95.Iapws95ParameterBlock()

# 4. Add unit models
m.fs.heater = Heater(property_package=m.fs.properties)

# 5. Set inputs
m.fs.heater.inlet.flow_mol.fix(100)  # mol/s
m.fs.heater.inlet.pressure.fix(101325)  # Pa
m.fs.heater.inlet.enth_mol.fix(5000)  # J/mol
m.fs.heater.heat_duty.fix(10000)  # W

# 6. Initialize
m.fs.heater.initialize()

# 7. Solve
from idaes.core.solvers import get_solver
solver = get_solver()
results = solver.solve(m)

# 8. Display results
m.fs.heater.outlet.display()
```

## Quick Reference - Common Tasks

**Create flowsheet:** `FlowsheetBlock(dynamic=False)` - Main container for process model
**Add unit model:** `m.fs.unit = UnitModel(property_package=m.fs.props)`
**Fix variables:** `m.fs.unit.inlet.flow_mol.fix(100)` - Specify known values
**Initialize model:** `m.fs.unit.initialize()` - Set up for solving
**Solve flowsheet:** `solver.solve(m)` - Get solution
**Run diagnostics:** `DiagnosticsToolbox(m).report_structural_issues()`
**Apply scaling:** `iscale.calculate_scaling_factors(m)`
**Optimize:** Set up objective and use solver or optimization tools

Detailed examples for all tasks in reference files.

## Task Routing

### Core Concepts and Architecture

**Route to:** `references/core-concepts.md`

**When:**
- Understanding IDAES architecture
- Learning about flowsheet structure
- Understanding control volumes
- Working with state blocks
- Understanding the modeling framework

**Key concepts:**
- FlowsheetBlock
- Property packages and state blocks
- Unit models and control volumes
- Ports and Arcs for connectivity
- Time domains for dynamic models

### Flowsheet Construction

**Route to:** `references/flowsheets.md`

**When:**
- Building process flowsheets
- Connecting unit operations
- Setting up material/energy streams
- Creating process flow diagrams
- Organizing hierarchical flowsheets

**Key components:**
- FlowsheetBlock creation
- Arc connections between units
- Port specification
- Degrees of freedom analysis
- Flowsheet visualization

### Property Packages

**Route to:** `references/property-packages.md`

**When:**
- Selecting thermodynamic methods
- Configuring component properties
- Setting up phase equilibrium
- Defining mixture properties
- Working with specialized systems (water/steam, combustion gases, etc.)

**Available packages:**
- IAPWS95 (water/steam)
- Ideal gas mixtures
- Modular property framework
- Cubic equations of state
- Electrolyte solutions (eNRTL)

### Unit Models

**Route to:** `references/unit-models.md`

**When:**
- Adding equipment to flowsheet
- Configuring unit operations
- Setting operating specifications
- Understanding model equations
- Customizing unit behavior

**Categories:**
- Generic models (heater, pump, compressor, etc.)
- Separations (flash, distillation, membranes)
- Reactors (stoichiometric, equilibrium, kinetic)
- Heat transfer (heat exchangers)
- Power generation specific equipment

### Generic Model Library

**Route to:** `references/generic-models.md`

**When:**
- Using standard unit operations
- Building general chemical processes
- Need mixers, splitters, heat exchangers
- Setting up separation equipment
- Working with reactors and pumps

**Common models:**
- Mixer, Splitter, Separator
- Heater, HeatExchanger
- Pump, Compressor, Turbine
- Flash, Distillation
- CSTR, PFR, Equilibrium Reactor

### Power Generation Models

**Route to:** `references/power-generation.md`

**When:**
- Modeling power plants
- Simulating combustion systems
- Working with steam cycles
- Analyzing turbine performance
- Boiler and heat recovery steam generator (HRSG) modeling

**Key models:**
- Boiler/Fireside models
- Steam turbines
- Heat recovery steam generators
- Feed water heaters
- Power plant flowsheets

### Gas-Solid Contactors

**Route to:** `references/gas-solid-models.md`

**When:**
- Modeling fluidized beds
- Simulating moving beds
- Working with solid particle flows
- Gas-solid reactions
- Adsorption processes

**Applications:**
- Chemical looping combustion
- Fixed bed reactors
- Fluidized bed reactors
- Moving bed systems

### Initialization

**Route to:** `references/initialization.md`

**When:**
- Preparing models for solving
- Dealing with initialization failures
- Setting up sequential initialization
- Using initialization strategies
- Troubleshooting convergence

**Strategies:**
- BlockTriangularizationInitializer
- Sequential initialization
- Custom initialization routines
- Using previous solutions
- Hierarchical initialization

### Solving and Convergence

**Route to:** `references/solving.md`

**When:**
- Solving flowsheet models
- Dealing with solver failures
- Improving convergence
- Understanding solver options
- Troubleshooting numerical issues

**Tools:**
- IPOPT solver configuration
- Solver selection
- Convergence diagnostics
- Solver output interpretation
- Handling solver failures

### Scaling

**Route to:** `references/scaling.md`

**When:**
- Improving numerical conditioning
- Addressing scaling issues
- Applying variable scaling
- Equation scaling
- Diagnosing ill-conditioned problems

**Key tools:**
- iscale module
- Automatic scaling factor calculation
- Manual scaling specification
- Scaling diagnostics
- Best practices for scaling

### Model Diagnostics

**Route to:** `references/diagnostics.md`

**When:**
- Debugging model issues
- Identifying structural problems
- Finding numerical issues
- Analyzing degrees of freedom
- Detecting equation singularities

**Diagnostic tools:**
- DiagnosticsToolbox
- Structural singularity detection
- Numerical singularity detection
- Degrees of freedom analysis
- SVD analysis for rank deficiency

### Optimization

**Route to:** `references/optimization.md`

**When:**
- Optimizing process design
- Minimizing operating costs
- Maximizing efficiency or production
- Multi-objective optimization
- Parameter studies and sensitivity analysis

**Capabilities:**
- Objective function definition
- Constraint specification
- Optimization solver configuration
- Parametric studies
- Design optimization

### Parameter Estimation and Data Reconciliation

**Route to:** `references/parameter-estimation.md`

**When:**
- Fitting model parameters to data
- Calibrating models
- Reconciling measured data
- Estimating kinetic parameters
- Model validation

**Tools:**
- parmest module
- Data reconciliation workflows
- Parameter estimation strategies
- Uncertainty quantification
- Model-data comparison

### Process Costing

**Route to:** `references/costing.md`

**When:**
- Calculating capital costs
- Estimating operating costs
- Economic analysis
- Optimization with cost objectives
- Techno-economic assessment

**Features:**
- Capital cost correlations
- Operating cost calculations
- Costing libraries for power generation
- Custom costing models

### Dynamic Modeling

**Route to:** `references/dynamic-modeling.md`

**When:**
- Time-dependent simulations
- Startup/shutdown analysis
- Control system design
- Dynamic optimization
- Process dynamics analysis

**Capabilities:**
- Dynamic flowsheets
- DAE systems
- Time discretization
- Dynamic solvers
- Control implementation

### Custom Model Development

**Route to:** `references/custom-models.md`

**When:**
- Creating new unit models
- Developing custom property packages
- Implementing specialized equations
- Extending existing models
- Research and development

**Topics:**
- Unit model templates
- Property package framework
- Custom constraints and expressions
- Model documentation
- Testing custom models

## Common Patterns

**Pattern 1: Simple Steady-State Flowsheet**
- Create flowsheet → Add property package → Add units → Connect with Arcs → Fix inputs → Initialize → Solve
- See `examples/simple_flowsheet.py` for complete workflow

**Pattern 2: Optimization Study**
- Build flowsheet → Initialize → Define objective → Set bounds → Optimize → Analyze results
- See `examples/optimization_example.py`

**Pattern 3: Parameter Estimation**
- Build model → Load experimental data → Define parameters → Run parmest → Analyze fit
- See `examples/parameter_estimation.py`

**Pattern 4: Sequential Modular Approach**
- Initialize units sequentially → Propagate information → Solve individual units → Solve full flowsheet
- See `examples/sequential_initialization.py`

All patterns detailed in `examples/` directory with complete code.

## Installation and Setup

### Install IDAES

```bash
# Create conda environment (recommended)
conda create -n idaes python=3.11
conda activate idaes

# Install IDAES
pip install idaes-pse

# Get solver binaries (IPOPT, etc.)
idaes get-extensions

# Verify installation
idaes --version
```

### Optional Components

```bash
# Install optional UI components
pip install idaes-pse[ui]

# Install OMLT for machine learning surrogates
pip install idaes-pse[omlt]

# Install for advanced grid optimization
pip install idaes-pse[grid]

# Install CoolProp for additional properties
pip install idaes-pse[coolprop]
```

### Testing Installation

```python
# Test IDAES import
import idaes
print(idaes.__version__)

# Test solver availability
from idaes.core.solvers import get_solver
solver = get_solver()
print(f"Solver: {solver}")
```

## Common Issues and Solutions

### Issue: Solver not found

**Problem:** `ApplicationError: No executable found for solver 'ipopt'`

**Solution:**
```bash
idaes get-extensions
# Or install solvers manually
conda install -c conda-forge ipopt
```

### Issue: Initialization fails

**Problem:** Unit model initialization does not converge

**Solution:**
1. Check degrees of freedom: `m.fs.unit.report_degrees_of_freedom()`
2. Use diagnostics: `DiagnosticsToolbox(m).report_structural_issues()`
3. Check input specifications are reasonable
4. Try sequential initialization
5. Review scaling factors

### Issue: Model doesn't solve

**Problem:** Solver returns non-optimal status

**Solution:**
```python
# Run diagnostics first
from idaes.core.util.model_diagnostics import DiagnosticsToolbox
dt = DiagnosticsToolbox(m)
dt.report_structural_issues()
dt.report_numerical_issues()

# Check and apply scaling
from idaes.core.util import scaling as iscale
iscale.calculate_scaling_factors(m)

# Try different solver options
solver = get_solver('ipopt', options={'tol': 1e-6, 'max_iter': 500})
```

### Issue: Poor numerical conditioning

**Problem:** Solver reports numerical difficulties or Jacobian issues

**Solution:**
1. Apply proper scaling using `iscale`
2. Check variable bounds are reasonable
3. Review units of measurement consistency
4. Use diagnostics to identify badly scaled variables
5. Consider variable transformations (e.g., log scaling for large range variables)

### Issue: Property package errors

**Problem:** Property calculations fail or return invalid values

**Solution:**
```python
# Check state variable specifications
m.fs.state.display()

# Ensure values are within valid ranges
# For IAPWS: T > 273.15 K, P > 611 Pa

# Check phase equilibrium assumptions are valid
# Use appropriate property package for your system
```

## Best Practices

### Model Development

- Start simple: build and test units individually before connecting
- Use degrees of freedom analysis regularly
- Always check model structure before solving
- Implement scaling from the start
- Document assumptions and specifications

### Initialization Strategy

- Initialize units in logical process order (upstream to downstream)
- Use results from simpler models to initialize complex ones
- Leverage IDAES initialization tools (BlockTriangularizationInitializer)
- Save successful initializations for reuse
- Consider hierarchical initialization for large flowsheets

### Numerical Robustness

- Apply consistent scaling across all variables
- Use appropriate property packages for your conditions
- Set reasonable variable bounds
- Monitor solver output and diagnostics
- Test with different initial guesses if convergence fails

### Performance Optimization

- Use appropriate solver tolerances (don't over-solve)
- Consider model simplifications where justified
- Use warm starts from previous solutions
- Profile code to identify bottlenecks
- Consider surrogate models for expensive property calculations

### Code Organization

- Use clear naming conventions for units and streams
- Organize complex flowsheets hierarchically
- Document specifications and assumptions
- Create reusable functions for common operations
- Use version control for model development

## Debugging Workflow

### Step 1: Check Model Structure
```python
# Degrees of freedom
m.fs.report_degrees_of_freedom()

# Structural diagnostics
from idaes.core.util.model_diagnostics import DiagnosticsToolbox
dt = DiagnosticsToolbox(m)
dt.report_structural_issues()
```

### Step 2: Verify Specifications
```python
# Display fixed variables
for v in m.component_data_objects(ctype=pyo.Var, descend_into=True):
    if v.fixed:
        print(f"{v}: {v.value}")

# Check for over/under specification
assert degrees_of_freedom(m) == 0
```

### Step 3: Check Scaling
```python
# Check scaling factors
from idaes.core.util import scaling as iscale
badly_scaled = iscale.badly_scaled_var_generator(m)
for var, scale in badly_scaled:
    print(f"{var}: scaling factor = {scale}")
```

### Step 4: Initialize Carefully
```python
# Try sequential initialization
try:
    m.fs.unit.initialize()
except:
    # If fails, check inputs and try with relaxed tolerances
    m.fs.unit.initialize(optarg={'tol': 1e-3})
```

### Step 5: Solve with Diagnostics
```python
solver = get_solver()
results = solver.solve(m, tee=True)  # tee=True shows solver output

# Check results
from pyomo.opt import TerminationCondition
if results.solver.termination_condition != TerminationCondition.optimal:
    print("Solve failed!")
    dt.report_numerical_issues()
```

## Examples Directory

See `examples/` for complete workflows:
- `simple_flowsheet.py` - Basic steady-state flowsheet
- `heater_example.py` - Simple heater with steam properties
- `flash_separation.py` - Flash separator example
- `heat_exchanger_network.py` - Multiple heat exchangers
- `distillation_column.py` - Separation process
- `power_plant_cycle.py` - Steam power cycle
- `optimization_example.py` - Process optimization
- `parameter_estimation.py` - Fitting parameters to data
- `dynamic_simulation.py` - Time-dependent model
- `custom_unit_model.py` - Creating custom models

## Reference Documentation

- `references/core-concepts.md` - Architecture and fundamental concepts
- `references/flowsheets.md` - Flowsheet construction and connectivity
- `references/property-packages.md` - Thermodynamic property modeling
- `references/unit-models.md` - Unit operation models overview
- `references/generic-models.md` - Generic model library details
- `references/power-generation.md` - Power generation specific models
- `references/gas-solid-models.md` - Gas-solid contactor models
- `references/initialization.md` - Initialization strategies and tools
- `references/solving.md` - Solving flowsheets and troubleshooting
- `references/scaling.md` - Scaling theory and application
- `references/diagnostics.md` - Model diagnostics and debugging
- `references/optimization.md` - Optimization workflows
- `references/parameter-estimation.md` - Parameter estimation and data reconciliation
- `references/costing.md` - Process economics and costing
- `references/dynamic-modeling.md` - Dynamic simulation
- `references/custom-models.md` - Developing custom models

## External Resources

- **Official docs:** https://idaes-pse.readthedocs.io/
- **GitHub:** https://github.com/IDAES/idaes-pse
- **Examples (Interactive):** https://idaes.github.io/examples-pse/latest/
- **Examples (Repository):** https://github.com/IDAES/examples-pse
- **Support:** idaes-support@idaes.org
- **Tutorials:** https://idaes-pse.readthedocs.io/en/stable/tutorials/
- **API Reference:** https://idaes-pse.readthedocs.io/en/stable/reference_guides/

## Key Differences from Other Process Simulators

**vs. Aspen Plus/HYSYS:**
- Open source and Python-based
- Full access to equations and customization
- Integration with optimization and machine learning
- Programmatic workflow automation

**vs. DWSIM:**
- More advanced optimization capabilities
- Better scaling and numerical tools
- Specialized for energy systems research
- Extensive diagnostics framework

**Strengths:**
- Equation-oriented solving
- Advanced optimization integration
- Custom model development
- Integration with Python ecosystem
- Diagnostic and scaling tools

**Considerations:**
- Requires Python programming knowledge
- Smaller library of pre-built unit models than commercial tools
- Less GUI support (primarily code-based)
- Learning curve for Pyomo framework
