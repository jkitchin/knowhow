# Graph Digitization Reference

This document covers methods for extracting numerical data from graphs, plots, and charts in scientific literature.

## Overview

Graph digitization (also called plot digitization or data extraction from figures) converts visual representations of data back into numerical values. This is essential when:

- Original data is not available in supplementary materials
- Comparing results across multiple publications
- Meta-analyses requiring raw data
- Reproducing or extending published results

## Methods

### 1. WebPlotDigitizer (Recommended for Manual Extraction)

**Website**: https://automeris.io/WebPlotDigitizer/

**Features**:
- Web-based and desktop applications
- Supports various plot types (XY, bar, polar, ternary, maps)
- Automatic data extraction algorithms
- Manual point selection
- Export to CSV, JSON
- Free and open source

**Workflow**:

1. **Upload Image**: Load graph image (PNG, JPG, PDF supported)

2. **Select Plot Type**:
   - 2D (X-Y) Plot: Standard scatter/line plots
   - 2D Bar Plot: Vertical/horizontal bar charts
   - Polar: Radial plots
   - Ternary: Three-component diagrams
   - Map: Geographic data

3. **Calibrate Axes**:
   - Click on 4 known points (2 on X-axis, 2 on Y-axis)
   - Enter their actual values
   - For log scales, select "Log" option

4. **Extract Data**:
   - **Manual**: Click on each data point
   - **Automatic (X Step)**: Algorithm detects points at regular X intervals
   - **Automatic (Averaging Window)**: Averages Y values in sliding window
   - **Color Detection**: Extract points by color

5. **Export**:
   - View extracted data in table
   - Download as CSV or copy to clipboard

**Tips for Better Results**:
- Use highest resolution image available
- Crop to remove surrounding text if possible
- For multiple data series, extract one at a time
- Double-check calibration points against known values
- Use zoom for precise point selection

---

### 2. PlotDigitizer

**Website**: https://plotdigitizer.com/

**Features**:
- Web-based tool
- Simple interface
- Supports linear, log, and other scales
- Multiple dataset extraction
- JSON/CSV export

**Workflow**:

1. Upload image
2. Define axes (click on axis points)
3. Set scale types (linear, log, date)
4. Add data points
5. Export results

---

### 3. LLM Vision for Graph Extraction

**Purpose**: Use multimodal LLMs (Claude Opus 5, GPT-4V) to interpret graphs and extract data.

**Best for**:
- Quick approximate extraction
- Batch processing
- Graphs with clear, discrete data points
- Trend identification

**Prompt Template**:
```
Analyze this scientific graph image and extract numerical data.

1. Identify the graph type (scatter, line, bar, etc.)
2. Describe the X-axis: label, units, range
3. Describe the Y-axis: label, units, range
4. Extract all visible data points as (x, y) pairs
5. If there are error bars, estimate their values
6. Identify any data series and their labels

Format the extracted data as:
```json
{
  "graph_type": "scatter",
  "x_axis": {"label": "", "units": "", "range": [min, max]},
  "y_axis": {"label": "", "units": "", "range": [min, max]},
  "data_series": [
    {
      "name": "Series 1",
      "points": [[x1, y1], [x2, y2], ...],
      "error_bars": [[x1_err, y1_err], ...]
    }
  ]
}
```
```

**Python Implementation**:
```python
import anthropic
import base64

def extract_graph_data_with_claude(image_path: str) -> dict:
    """Use Claude to extract data from a graph image."""
    client = anthropic.Anthropic()

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine media type
    if image_path.endswith(".png"):
        media_type = "image/png"
    elif image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        media_type = "image/jpeg"
    else:
        media_type = "image/png"

    prompt = """Analyze this scientific graph and extract numerical data.

1. Identify the graph type
2. Extract axis labels, units, and ranges
3. Extract all visible data points as (x, y) pairs
4. Note any error bars or uncertainty indicators

Return the data as JSON with this structure:
{
  "graph_type": "type",
  "x_axis": {"label": "", "units": "", "range": [min, max], "scale": "linear|log"},
  "y_axis": {"label": "", "units": "", "range": [min, max], "scale": "linear|log"},
  "data_series": [
    {
      "name": "series name",
      "points": [[x1, y1], [x2, y2], ...],
      "uncertainty": "description of error bars if present"
    }
  ],
  "notes": "any additional observations"
}
"""

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # Parse JSON from response
    import json
    import re

    text = response.content[0].text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return {"error": "Could not parse JSON", "raw": text}
```

**Limitations of LLM Vision**:
- Approximate values (limited precision)
- May miss overlapping points
- Struggles with dense plots
- Inconsistent with small features
- Always validate against source

---

### 4. Programmatic Approaches

#### Using OpenCV for Line Detection

```python
import cv2
import numpy as np

def extract_line_plot_points(image_path: str, axis_bounds: dict) -> list:
    """
    Extract points from a simple line plot using color detection.

    axis_bounds: {
        'x_pixel_range': (x_min_px, x_max_px),
        'y_pixel_range': (y_min_px, y_max_px),
        'x_data_range': (x_min, x_max),
        'y_data_range': (y_min, y_max)
    }
    """
    # Load image
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define color range for data line (adjust for your plot)
    # Example: blue line
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    points_pixel = []
    for contour in contours:
        for point in contour:
            x, y = point[0]
            points_pixel.append((x, y))

    # Convert pixel coordinates to data coordinates
    def pixel_to_data(px, py):
        x_px_min, x_px_max = axis_bounds['x_pixel_range']
        y_px_min, y_px_max = axis_bounds['y_pixel_range']
        x_min, x_max = axis_bounds['x_data_range']
        y_min, y_max = axis_bounds['y_data_range']

        x = x_min + (px - x_px_min) / (x_px_max - x_px_min) * (x_max - x_min)
        # Note: Y axis is inverted in images
        y = y_max - (py - y_px_min) / (y_px_max - y_px_min) * (y_max - y_min)
        return (x, y)

    points_data = [pixel_to_data(px, py) for px, py in points_pixel]

    # Sort by x coordinate
    points_data.sort(key=lambda p: p[0])

    return points_data
```

#### Using matplotlib for Interactive Digitization

```python
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class InteractiveDigitizer:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.calibration_points = []
        self.data_points = []
        self.mode = 'calibrate'  # or 'digitize'

    def run(self):
        """Run interactive digitization session."""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        img = mpimg.imread(self.image_path)
        self.ax.imshow(img)
        self.ax.set_title("Click 4 calibration points (x_min, x_max, y_min, y_max)")

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        plt.show()

        return self.data_points

    def onclick(self, event):
        if event.inaxes != self.ax:
            return

        if self.mode == 'calibrate':
            self.calibration_points.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'ro', markersize=10)
            self.fig.canvas.draw()

            if len(self.calibration_points) == 4:
                self.mode = 'digitize'
                self.ax.set_title("Click on data points. Close window when done.")
                # Get calibration values
                self.setup_calibration()

        elif self.mode == 'digitize':
            # Convert to data coordinates
            x_data, y_data = self.pixel_to_data(event.xdata, event.ydata)
            self.data_points.append((x_data, y_data))
            self.ax.plot(event.xdata, event.ydata, 'gx', markersize=8)
            self.fig.canvas.draw()
            print(f"Point: ({x_data:.4f}, {y_data:.4f})")

    def setup_calibration(self):
        """Prompt for calibration values."""
        print("Enter calibration values:")
        self.x_min_val = float(input("X-axis minimum value: "))
        self.x_max_val = float(input("X-axis maximum value: "))
        self.y_min_val = float(input("Y-axis minimum value: "))
        self.y_max_val = float(input("Y-axis maximum value: "))

        # Store pixel positions
        self.x_min_px = self.calibration_points[0][0]
        self.x_max_px = self.calibration_points[1][0]
        self.y_min_px = self.calibration_points[2][1]
        self.y_max_px = self.calibration_points[3][1]

    def pixel_to_data(self, px, py):
        x = self.x_min_val + (px - self.x_min_px) / (self.x_max_px - self.x_min_px) * (self.x_max_val - self.x_min_val)
        y = self.y_max_val - (py - self.y_max_px) / (self.y_min_px - self.y_max_px) * (self.y_max_val - self.y_min_val)
        return (x, y)
```

---

## Best Practices

### 1. Image Quality

- **Resolution**: Use highest available (300+ DPI preferred)
- **Format**: PNG preferred over JPEG (no compression artifacts)
- **Cropping**: Remove legends, titles if they interfere
- **Contrast**: Ensure data points are clearly visible

### 2. Calibration

- **Use exact values**: Pick axis ticks with known values
- **Span full range**: Calibration points should cover entire axis
- **Check scaling**: Verify linear vs. logarithmic axes
- **Validate**: Test calibration with known points before proceeding

### 3. Data Extraction

- **Systematic approach**: Extract points in consistent order
- **Multiple series**: Handle one series at a time
- **Overlapping points**: Zoom in for precision
- **Error bars**: Note if symmetric or asymmetric

### 4. Validation

```python
def validate_extracted_data(extracted: list, expected_range: tuple, n_points_expected: int = None):
    """Validate extracted data against expectations."""
    issues = []

    # Check range
    x_vals = [p[0] for p in extracted]
    y_vals = [p[1] for p in extracted]

    x_min_exp, x_max_exp, y_min_exp, y_max_exp = expected_range

    if min(x_vals) < x_min_exp * 0.9 or max(x_vals) > x_max_exp * 1.1:
        issues.append(f"X values outside expected range: {min(x_vals):.2f} to {max(x_vals):.2f}")

    if min(y_vals) < y_min_exp * 0.9 or max(y_vals) > y_max_exp * 1.1:
        issues.append(f"Y values outside expected range: {min(y_vals):.2f} to {max(y_vals):.2f}")

    # Check point count
    if n_points_expected and abs(len(extracted) - n_points_expected) > n_points_expected * 0.1:
        issues.append(f"Point count mismatch: expected ~{n_points_expected}, got {len(extracted)}")

    # Check monotonicity if expected
    if x_vals != sorted(x_vals):
        issues.append("X values not monotonically increasing")

    return len(issues) == 0, issues
```

### 5. Documentation

Always record:
- Source publication (DOI, figure number)
- Extraction method used
- Calibration points and values
- Any assumptions made
- Estimated uncertainty

```python
extraction_record = {
    "source": {
        "doi": "10.1234/journal.2024.001",
        "figure": "Figure 3a",
        "description": "Temperature dependence of conductivity"
    },
    "extraction": {
        "method": "WebPlotDigitizer 4.6",
        "date": "2025-01-18",
        "extractor": "J. Doe"
    },
    "calibration": {
        "x_axis": {"label": "Temperature", "units": "K", "points": [[100, 100], [400, 400]]},
        "y_axis": {"label": "Conductivity", "units": "S/cm", "points": [[0.1, 0.1], [10, 10]]}
    },
    "data": [[100, 0.15], [150, 0.32], [200, 0.78], ...],
    "uncertainty": "Estimated +/- 2% due to point selection",
    "notes": "Data extracted from low-resolution figure; recommend verification with authors"
}
```

## Accuracy Considerations

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Image resolution | Point positioning error | Use highest quality source |
| Axis calibration | Systematic error | Use exact tick values |
| Point overlap | Missing data | Zoom, extract series separately |
| Log scales | Non-linear error | Verify calibration at multiple points |
| Color similarity | Confusion | Adjust color detection thresholds |
| Human fatigue | Random errors | Take breaks, verify subset |

## References

- [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) - Rohatgi, A.
- [PlotDigitizer Validation Study](https://doi.org/10.1016/j.jbiomech.2011.07.024) - Near-perfect validity/reliability
- [Best Practices for Data Extraction](https://www.cochrane.org/MR000003/METHOD_data-extraction-and-management) - Cochrane Handbook
