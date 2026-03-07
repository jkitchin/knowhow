---
name: python-plotting
description: Comprehensive plotting and visualization in Python - matplotlib (static publication-quality plots), seaborn (statistical visualization), and plotly (interactive plots); includes plot types, customization, best practices, and library selection guidance
allowed-tools: ["*"]
---

# Python Plotting & Visualization

## Overview

Master data visualization in Python through three complementary libraries: **matplotlib** (foundational static plots), **seaborn** (statistical visualization), and **plotly** (interactive graphics). Each library has distinct strengths, and knowing when to use which—or how to combine them—is key to effective data communication.

**Core value:** Create publication-quality static plots, insightful statistical graphics, and interactive dashboards with the right tool for each visualization need.

## Library Selection Guide

### Matplotlib - The Foundation

**Use when:**
- Need fine-grained control over every plot element
- Creating publication-quality static figures
- Building custom visualizations not available elsewhere
- Working with low-level plotting requirements
- Need maximum compatibility (most widely supported)

**Strengths:**
- Complete control over every visual element
- Mature, stable, extensively documented
- Foundation for seaborn and other libraries
- Export to any format (PDF, SVG, PNG, etc.)
- Extensive customization options

**Weaknesses:**
- Verbose for common statistical plots
- Steeper learning curve for complex plots
- Static output (no interactivity)
- Default aesthetics less modern

### Seaborn - Statistical Visualization

**Use when:**
- Creating statistical plots (distributions, correlations, regressions)
- Need attractive defaults with minimal code
- Working with pandas DataFrames
- Want automatic statistical estimation
- Need faceted/multi-panel plots

**Strengths:**
- Concise syntax for statistical plots
- Beautiful default themes
- Built-in statistical estimation
- Seamless pandas integration
- FacetGrid for complex multi-panel layouts

**Weaknesses:**
- Less control than matplotlib
- Limited to statistical plot types
- Static output only
- Requires understanding of underlying matplotlib for deep customization

### Plotly - Interactive Visualization

**Use when:**
- Need interactive plots (zoom, hover, pan)
- Building dashboards or web apps
- Want 3D visualizations
- Need animations
- Sharing exploratory analysis

**Strengths:**
- Rich interactivity out-of-the-box
- Beautiful defaults
- 3D and geographic plotting
- Integration with Dash for web apps
- Export to HTML for sharing

**Weaknesses:**
- Larger file sizes
- Less control than matplotlib for publications
- Different API paradigm
- Not ideal for static publication figures

### Quick Decision Tree

```
Need interactivity?
├─ Yes → Plotly
└─ No → Statistical plot?
    ├─ Yes → Seaborn (can customize with matplotlib)
    └─ No → Complex customization needed?
        ├─ Yes → Matplotlib
        └─ No → Seaborn or Matplotlib (preference)
```

## Matplotlib - Foundational Plotting

### Two APIs: pyplot vs Object-Oriented

**pyplot (MATLAB-style, implicit state):**
```python
import matplotlib.pyplot as plt

# Quick and interactive
plt.plot([1, 2, 3], [1, 4, 9])
plt.xlabel('x')
plt.ylabel('y')
plt.title('Simple Plot')
plt.show()
```

**Object-Oriented (explicit, recommended for complex plots):**
```python
import matplotlib.pyplot as plt

# Explicit control
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Simple Plot')
plt.show()
```

**Recommendation:** Use OO API for scripts, functions, and complex plots. Use pyplot for quick interactive exploration.

### Figure Anatomy

```python
import matplotlib.pyplot as plt
import numpy as np

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# fig = Figure (entire window)
# axes = array of Axes (individual plots)

# Access individual axes
ax1 = axes[0, 0]  # Top left
ax2 = axes[0, 1]  # Top right
ax3 = axes[1, 0]  # Bottom left
ax4 = axes[1, 1]  # Bottom right

# Plot on each axes
ax1.plot([1, 2, 3], [1, 4, 9])
ax2.scatter([1, 2, 3], [1, 4, 9])
ax3.bar([1, 2, 3], [1, 4, 9])
ax4.hist(np.random.randn(1000))

# Adjust layout
plt.tight_layout()
plt.show()
```

### Common Plot Types

**Line Plot:**
```python
fig, ax = plt.subplots()

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

ax.plot(x, y1, label='sin(x)', linewidth=2, color='blue', linestyle='-')
ax.plot(x, y2, label='cos(x)', linewidth=2, color='red', linestyle='--')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Trigonometric Functions')
ax.legend()
ax.grid(True, alpha=0.3)
plt.show()
```

**Scatter Plot:**
```python
fig, ax = plt.subplots()

x = np.random.randn(100)
y = 2*x + np.random.randn(100)*0.5
colors = np.random.rand(100)
sizes = 100 * np.random.rand(100)

scatter = ax.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Scatter Plot with Color and Size')

# Add colorbar
plt.colorbar(scatter, ax=ax, label='Color Value')
plt.show()
```

**Bar Plot:**
```python
fig, ax = plt.subplots()

categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]

bars = ax.bar(categories, values, color=['red', 'blue', 'green', 'orange', 'purple'])

# Annotate bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value}',
            ha='center', va='bottom')

ax.set_ylabel('Values')
ax.set_title('Bar Chart')
plt.show()
```

**Histogram:**
```python
fig, ax = plt.subplots()

data = np.random.randn(1000)

ax.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')

ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
ax.set_title('Histogram')
ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label='Mean')
ax.legend()
plt.show()
```

**Subplots with Shared Axes:**
```python
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

ax1.plot(x, y1)
ax1.set_ylabel('sin(x)')
ax1.grid(True)

ax2.plot(x, y2, color='red')
ax2.set_xlabel('x')
ax2.set_ylabel('cos(x)')
ax2.grid(True)

plt.tight_layout()
plt.show()
```

### Customization

**Styles:**
```python
import matplotlib.pyplot as plt

# List available styles
print(plt.style.available)

# Use a style
plt.style.use('seaborn-v0_8-darkgrid')
# or
with plt.style.context('ggplot'):
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.show()
```

**Colors and Colormaps:**
```python
# Named colors
ax.plot(x, y, color='steelblue')
ax.plot(x, y, color='#FF6347')  # Hex
ax.plot(x, y, color=(0.2, 0.4, 0.6))  # RGB

# Colormaps
from matplotlib import cm

colors = cm.viridis(np.linspace(0, 1, 10))
for i, color in enumerate(colors):
    ax.plot([i, i+1], [0, 1], color=color)
```

**Markers and Line Styles:**
```python
ax.plot(x, y,
        marker='o',           # Circle markers
        markersize=8,
        markerfacecolor='red',
        markeredgecolor='black',
        markeredgewidth=2,
        linestyle='--',       # Dashed line
        linewidth=2,
        color='blue')
```

**Legends:**
```python
ax.plot(x, y1, label='Data 1')
ax.plot(x, y2, label='Data 2')

ax.legend(
    loc='upper right',    # or 'best', 'center', etc.
    frameon=True,
    shadow=True,
    fancybox=True,
    fontsize=12
)
```

**Annotations:**
```python
ax.plot(x, y)

# Annotate a point
ax.annotate(
    'Maximum',
    xy=(x[50], y[50]),       # Point to annotate
    xytext=(x[50]+1, y[50]+1),  # Text location
    arrowprops=dict(arrowstyle='->', color='red', lw=2),
    fontsize=12,
    color='red'
)
```

**Saving Figures:**
```python
# High-resolution PNG
fig.savefig('plot.png', dpi=300, bbox_inches='tight')

# Vector formats for publications
fig.savefig('plot.pdf', bbox_inches='tight')
fig.savefig('plot.svg', bbox_inches='tight')

# Transparent background
fig.savefig('plot.png', transparent=True, bbox_inches='tight')
```

## Seaborn - Statistical Visualization

### Basic Setup

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Set theme
sns.set_theme(style='whitegrid')  # whitegrid, darkgrid, white, dark, ticks

# Load example dataset
tips = sns.load_dataset('tips')  # Built-in datasets for examples
```

### Distribution Plots

**Histogram with KDE:**
```python
fig, ax = plt.subplots()

sns.histplot(data=tips, x='total_bill', kde=True, ax=ax)

ax.set_title('Distribution of Total Bill')
plt.show()
```

**KDE Plot:**
```python
fig, ax = plt.subplots()

sns.kdeplot(data=tips, x='total_bill', hue='time', fill=True, ax=ax)

ax.set_title('Total Bill Distribution by Time')
plt.show()
```

**Distribution Plot (ECDF):**
```python
fig, ax = plt.subplots()

sns.ecdfplot(data=tips, x='total_bill', hue='sex', ax=ax)

ax.set_title('Cumulative Distribution of Total Bill')
plt.show()
```

### Categorical Plots

**Box Plot:**
```python
fig, ax = plt.subplots(figsize=(10, 6))

sns.boxplot(data=tips, x='day', y='total_bill', hue='sex', ax=ax)

ax.set_title('Total Bill by Day and Sex')
plt.show()
```

**Violin Plot:**
```python
fig, ax = plt.subplots(figsize=(10, 6))

sns.violinplot(data=tips, x='day', y='total_bill', hue='sex',
               split=True, ax=ax)

ax.set_title('Total Bill Distribution by Day')
plt.show()
```

**Strip Plot / Swarm Plot:**
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Strip plot (with jitter)
sns.stripplot(data=tips, x='day', y='total_bill', hue='sex',
              dodge=True, alpha=0.6, ax=axes[0])
axes[0].set_title('Strip Plot')

# Swarm plot (no overlap)
sns.swarmplot(data=tips, x='day', y='total_bill', hue='sex',
              dodge=True, ax=axes[1])
axes[1].set_title('Swarm Plot')

plt.tight_layout()
plt.show()
```

**Bar Plot with Error Bars:**
```python
fig, ax = plt.subplots()

sns.barplot(data=tips, x='day', y='total_bill', hue='sex',
            errorbar=("ci", 95),
            ax=ax)

ax.set_title('Average Total Bill by Day')
plt.show()
```

### Relational Plots

**Scatter Plot:**
```python
fig, ax = plt.subplots(figsize=(10, 6))

sns.scatterplot(data=tips, x='total_bill', y='tip',
                hue='time', size='size', style='sex',
                sizes=(50, 200), alpha=0.6, ax=ax)

ax.set_title('Tip vs Total Bill')
plt.show()
```

**Line Plot:**
```python
# Create time series data
fmri = sns.load_dataset('fmri')

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(data=fmri, x='timepoint', y='signal',
             hue='event', style='region', ax=ax)

ax.set_title('fMRI Signal Over Time')
plt.show()
```

### Regression Plots

**Linear Regression:**
```python
fig, ax = plt.subplots()

sns.regplot(data=tips, x='total_bill', y='tip', ax=ax)

ax.set_title('Linear Regression: Tip vs Total Bill')
plt.show()
```

**Residual Plot:**
```python
fig, ax = plt.subplots()

sns.residplot(data=tips, x='total_bill', y='tip', ax=ax)

ax.set_title('Residual Plot')
ax.axhline(0, color='red', linestyle='--')
plt.show()
```

### Heatmaps and Matrices

**Correlation Heatmap:**
```python
fig, ax = plt.subplots(figsize=(8, 6))

# Compute correlation matrix
corr = tips[['total_bill', 'tip', 'size']].corr()

sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, ax=ax)

ax.set_title('Correlation Matrix')
plt.show()
```

**Clustermap:**
```python
# Hierarchical clustering heatmap
iris = sns.load_dataset('iris')
iris_data = iris.drop('species', axis=1)

g = sns.clustermap(iris_data.T, cmap='viridis',
                   standard_scale=1, figsize=(8, 8))
plt.show()
```

### Multi-Panel Plots

**FacetGrid:**
```python
# Create grid of plots
g = sns.FacetGrid(tips, col='time', row='sex',
                  margin_titles=True, height=4)

# Map plot type to grid
g.map(sns.scatterplot, 'total_bill', 'tip', alpha=0.6)

# Customize
g.set_axis_labels('Total Bill', 'Tip')
g.set_titles(col_template="{col_name}", row_template="{row_name}")
g.add_legend()

plt.show()
```

**PairGrid:**
```python
# Pairwise relationships
iris = sns.load_dataset('iris')

g = sns.PairGrid(iris, hue='species', height=2.5)
g.map_upper(sns.scatterplot)
g.map_lower(sns.kdeplot)
g.map_diag(sns.histplot)
g.add_legend()

plt.show()
```

**Pairplot (simpler):**
```python
sns.pairplot(iris, hue='species', diag_kind='kde', height=2.5)
plt.show()
```

### Themes and Color Palettes

**Setting Themes:**
```python
# Theme styles
sns.set_theme(style='whitegrid')  # white, dark, whitegrid, darkgrid, ticks

# Context (scales elements)
sns.set_context('talk')  # paper, notebook, talk, poster

# Combined
sns.set_theme(style='darkgrid', context='poster',
              palette='deep', font_scale=1.2)
```

**Color Palettes:**
```python
# Qualitative (categorical)
sns.set_palette('deep')  # deep, muted, pastel, bright, dark, colorblind

# Sequential
sns.set_palette('Blues')

# Diverging
sns.set_palette('coolwarm')

# Custom
custom_palette = ['#FF6347', '#4682B4', '#32CD32']
sns.set_palette(custom_palette)

# View palette
# sns.palplot() is deprecated; use .plot() method instead
sns.color_palette('husl', 10).plot()
plt.show()
```

## Plotly - Interactive Visualization

### Plotly Express - High-Level API

**Scatter Plot:**
```python
import plotly.express as px

df = px.data.iris()

fig = px.scatter(df, x='sepal_width', y='sepal_length',
                 color='species', size='petal_length',
                 hover_data=['petal_width'],
                 title='Iris Dataset')

fig.show()
```

**Line Plot:**
```python
df = px.data.gapminder()

fig = px.line(df[df['country'] == 'Canada'],
              x='year', y='gdpPercap',
              title='Canada GDP per Capita')

fig.show()
```

**Bar Chart:**
```python
df = px.data.tips()

fig = px.bar(df, x='day', y='total_bill', color='sex',
             barmode='group',  # or 'stack', 'overlay'
             title='Total Bill by Day and Sex')

fig.show()
```

**Histogram:**
```python
fig = px.histogram(df, x='total_bill', color='sex',
                   marginal='box',  # or 'violin', 'rug'
                   title='Total Bill Distribution')

fig.show()
```

**Box Plot:**
```python
fig = px.box(df, x='day', y='total_bill', color='sex',
             title='Total Bill by Day')

fig.show()
```

**Heatmap:**
```python
import numpy as np

z = np.random.randn(20, 20)

fig = px.imshow(z, color_continuous_scale='RdBu_r',
                title='Heatmap')

fig.show()
```

**3D Scatter:**
```python
df = px.data.iris()

fig = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_length',
                    color='species', size='petal_width',
                    title='3D Iris Dataset')

fig.show()
```

**Animated Plots:**
```python
df = px.data.gapminder()

fig = px.scatter(df, x='gdpPercap', y='lifeExp',
                 animation_frame='year',
                 animation_group='country',
                 size='pop', color='continent',
                 hover_name='country',
                 log_x=True, size_max=60,
                 range_x=[100, 100000], range_y=[25, 90],
                 title='Gapminder Data Over Time')

fig.show()
```

### Graph Objects - Low-Level API

**Basic Scatter:**
```python
import plotly.graph_objects as go

x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers+lines'))

fig.update_layout(
    title='Custom Scatter Plot',
    xaxis_title='X Axis',
    yaxis_title='Y Axis'
)

fig.show()
```

**Multiple Traces:**
```python
fig = go.Figure()

# Add multiple traces
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 4, 9],
                         mode='lines', name='Series 1'))
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[2, 5, 10],
                         mode='lines+markers', name='Series 2'))

fig.update_layout(title='Multiple Series')
fig.show()
```

**Subplots:**
```python
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Plot 1', 'Plot 2', 'Plot 3', 'Plot 4')
)

# Add traces to specific subplots
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 4, 9]), row=1, col=1)
fig.add_trace(go.Bar(x=[1, 2, 3], y=[2, 5, 8]), row=1, col=2)
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[3, 6, 9]), row=2, col=1)
fig.add_trace(go.Box(y=[1, 2, 3, 4, 5, 6, 7]), row=2, col=2)

fig.update_layout(height=600, showlegend=False, title_text='Subplots')
fig.show()
```

**Interactive Features:**
```python
fig = go.Figure()

fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13]))

# Add dropdown menu
fig.update_layout(
    updatemenus=[
        dict(
            buttons=list([
                dict(label="Linear",
                     method="relayout",
                     args=[{"yaxis.type": "linear"}]),
                dict(label="Log",
                     method="relayout",
                     args=[{"yaxis.type": "log"}])
            ]),
            direction="down",
        )
    ]
)

fig.show()
```

**Exporting:**
```python
# To HTML
fig.write_html('plot.html')

# To static image (requires kaleido)
fig.write_image('plot.png', width=1200, height=800)
fig.write_image('plot.pdf')
```

## Integration Patterns

### Seaborn with Matplotlib Customization

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Create seaborn plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=tips, x='day', y='total_bill', ax=ax)

# Customize with matplotlib
ax.set_title('Customized Seaborn Plot', fontsize=16, fontweight='bold')
ax.set_xlabel('Day of Week', fontsize=12)
ax.set_ylabel('Total Bill ($)', fontsize=12)
ax.grid(axis='y', alpha=0.3)

# Add custom annotation
ax.text(0.5, 0.95, 'Custom annotation',
        transform=ax.transAxes, ha='center')

plt.tight_layout()
plt.show()
```

### Plotly with Pandas

```python
import pandas as pd
import plotly.express as px

# Pandas DataFrame
df = pd.DataFrame({
    'x': range(10),
    'y': [i**2 for i in range(10)],
    'category': ['A', 'B'] * 5
})

# Direct plotting from DataFrame
fig = px.line(df, x='x', y='y', color='category')
fig.show()
```

## Best Practices

### 1. Choose Appropriate Plot Type

**Distributions:**
- Histogram, KDE plot, box plot, violin plot
- Use: Understanding data spread and shape

**Comparisons:**
- Bar chart, box plot, strip plot
- Use: Comparing groups or categories

**Relationships:**
- Scatter plot, line plot, regression plot
- Use: Showing correlations or trends

**Compositions:**
- Stacked bar, pie chart (use sparingly), treemap
- Use: Part-to-whole relationships

**Time Series:**
- Line plot, area chart
- Use: Temporal patterns

### 2. Design Principles

**Less is More:**
```python
# Bad: Too much decoration
fig, ax = plt.subplots()
ax.plot(x, y, linewidth=5, color='red', linestyle='--',
        marker='o', markersize=15, markerfacecolor='yellow')
ax.grid(True, linewidth=2, color='blue')
ax.set_facecolor('lightgray')

# Good: Clean and focused
fig, ax = plt.subplots()
ax.plot(x, y, linewidth=2, color='steelblue')
ax.grid(True, alpha=0.3)
```

**Effective Use of Color:**
```python
# Use color purposefully
# - Categorical: Distinct hues
# - Sequential: Single hue gradient
# - Diverging: Two hues from neutral center

# Colorblind-friendly palettes
sns.set_palette('colorblind')
# or
import plotly.express as px
fig = px.scatter(df, x='x', y='y', color='category',
                 color_discrete_sequence=px.colors.qualitative.Safe)
```

**Readable Text:**
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)

# Clear, appropriately sized text
ax.set_title('Clear Title', fontsize=16, pad=20)
ax.set_xlabel('X Axis Label', fontsize=12)
ax.set_ylabel('Y Axis Label', fontsize=12)
ax.tick_params(labelsize=10)
```

### 3. Consistent Styling

```python
# Set style once at beginning
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100

# All plots will use these settings
```

### 4. Save High-Quality Figures

```python
# For publications
fig.savefig('figure.pdf', dpi=300, bbox_inches='tight')
fig.savefig('figure.png', dpi=300, bbox_inches='tight')

# For presentations
fig.savefig('figure.png', dpi=150, bbox_inches='tight')

# For web
fig.savefig('figure.png', dpi=96, bbox_inches='tight', optimize=True)
```

## Common Gotchas

### 1. Figure Size and DPI

```python
# ❌ Bad: Default size too small
fig, ax = plt.subplots()

# ✅ Good: Set appropriate size
fig, ax = plt.subplots(figsize=(10, 6))  # Width, height in inches
```

### 2. Overlapping Labels

```python
# ❌ Bad: Labels overlap
fig, ax = plt.subplots()
ax.bar(range(10), values)
ax.set_xticklabels(long_labels)

# ✅ Good: Rotate labels
ax.set_xticklabels(long_labels, rotation=45, ha='right')

# ✅ Better: Use tight_layout
plt.tight_layout()
```

### 3. Color Mapping Consistency

```python
# ❌ Bad: Inconsistent colors across plots
sns.scatterplot(data=df1, x='x', y='y', hue='category')
sns.scatterplot(data=df2, x='x', y='y', hue='category')  # Different colors!

# ✅ Good: Define palette
palette = {'A': 'red', 'B': 'blue', 'C': 'green'}
sns.scatterplot(data=df1, x='x', y='y', hue='category', palette=palette)
sns.scatterplot(data=df2, x='x', y='y', hue='category', palette=palette)
```

### 4. Seaborn Doesn't Return Axes

```python
# ❌ Bad: Expecting return value
ax = sns.boxplot(data=df, x='x', y='y')  # Returns Axes, but...

# ✅ Good: Pass axes explicitly
fig, ax = plt.subplots()
sns.boxplot(data=df, x='x', y='y', ax=ax)
ax.set_title('My Title')  # Now can customize
```

### 5. Plotly Memory with Large Datasets

```python
# ❌ Bad: Plotting millions of points
fig = px.scatter(huge_df)  # Slow, large file

# ✅ Good: Sample or aggregate
fig = px.scatter(huge_df.sample(10000))
# or use datashader for huge datasets
```

### 6. Matplotlib State Machine Confusion

```python
# ❌ Bad: Mixing pyplot and OO API
plt.figure()
ax = plt.gca()
ax.plot(x, y)
plt.xlabel('x')  # State machine call
ax.set_ylabel('y')  # Object-oriented call

# ✅ Good: Be consistent
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel('x')
ax.set_ylabel('y')
```

## Quick Reference

### Matplotlib

```python
# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot types
ax.plot(x, y)                    # Line
ax.scatter(x, y)                 # Scatter
ax.bar(x, y)                     # Bar
ax.hist(data, bins=30)           # Histogram
ax.boxplot([data1, data2])       # Box plot

# Customization
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_title('Title')
ax.legend()
ax.grid(True)

# Save
fig.savefig('plot.png', dpi=300, bbox_inches='tight')
```

### Seaborn

```python
import seaborn as sns

# Set theme
sns.set_theme(style='whitegrid')

# Plot types
sns.histplot(data=df, x='col')
sns.scatterplot(data=df, x='x', y='y', hue='category')
sns.boxplot(data=df, x='category', y='value')
sns.heatmap(corr_matrix, annot=True)

# Multi-panel
sns.pairplot(df, hue='species')
```

### Plotly Express

```python
import plotly.express as px

# Plot types
fig = px.scatter(df, x='x', y='y', color='category')
fig = px.line(df, x='x', y='y')
fig = px.bar(df, x='x', y='y', color='category')
fig = px.histogram(df, x='value')
fig = px.box(df, x='category', y='value')

# Show/Save
fig.show()
fig.write_html('plot.html')
```

## Installation

```bash
# Matplotlib
pip install matplotlib

# Seaborn
pip install seaborn

# Plotly
pip install plotly

# For static image export (plotly)
pip install kaleido

# All together
pip install matplotlib seaborn plotly kaleido
```

## Additional Resources

- **Matplotlib:** https://matplotlib.org/stable/gallery/index.html
- **Seaborn:** https://seaborn.pydata.org/examples/index.html
- **Plotly:** https://plotly.com/python/
- **Python Graph Gallery:** https://python-graph-gallery.com/
- **From Data to Viz:** https://www.data-to-viz.com/

## Related Skills

- `pycse` - Scientific computing with confidence intervals for plots
- `python-ase` - Atomic structure visualization
- `python-best-practices` - Code quality for visualization scripts
