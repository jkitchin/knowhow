# Example: Graph Digitization Workflow

This example demonstrates extracting numerical data from scientific graphs and plots.

## Scenario

You have a figure from a published paper showing:
- A scatter plot of material properties vs. temperature
- Multiple data series with different markers
- Error bars on some points
- A fitted line/curve

Goal: Extract the underlying data points for analysis or reproduction.

## Method 1: WebPlotDigitizer (Manual, High Accuracy)

WebPlotDigitizer is the gold standard for accurate graph digitization.

### Step-by-Step Workflow

1. **Open WebPlotDigitizer**: https://automeris.io/WebPlotDigitizer/

2. **Load Image**:
   - Click "File" → "Load Image"
   - Select your graph image (PNG, JPG, or PDF page)

3. **Select Plot Type**:
   - Choose "2D (X-Y) Plot" for standard scatter/line plots
   - Click "Align Axes"

4. **Calibrate Axes**:
   ```
   Step 1: Click on a known point on X-axis (e.g., X=0)
   Step 2: Click on another known point on X-axis (e.g., X=100)
   Step 3: Click on a known point on Y-axis (e.g., Y=0)
   Step 4: Click on another known point on Y-axis (e.g., Y=10)

   Enter the actual values for each point when prompted.

   For log scales: Check "Log Scale" checkbox for the appropriate axis.
   ```

5. **Add Dataset**: Click "Add Dataset" for each data series

6. **Extract Points**:
   - **Manual**: Click on each data point
   - **Automatic X Step**: Algorithm detects points at regular X intervals
   - **Color Detection**: Select data color to auto-detect points

7. **Export**: "View Data" → "Download .CSV"

### Tips for Best Results

```
- Use highest resolution image available (extract from PDF if possible)
- Zoom in for precise point selection (use mouse wheel)
- For dense data, extract points systematically (left to right)
- Extract each data series as a separate dataset
- Double-check calibration using a known intermediate point
```

## Method 2: LLM Vision Extraction

For quick approximate extraction or batch processing.

```python
import anthropic
import base64
import json
import re

def extract_graph_with_llm(image_path: str) -> dict:
    """Extract data from graph using Claude's vision capabilities."""

    client = anthropic.Anthropic()

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine media type
    if image_path.lower().endswith(".png"):
        media_type = "image/png"
    elif image_path.lower().endswith((".jpg", ".jpeg")):
        media_type = "image/jpeg"
    else:
        media_type = "image/png"

    prompt = """Analyze this scientific graph and extract numerical data.

Please provide:

1. **Graph Description**:
   - Type (scatter, line, bar, etc.)
   - What is being plotted

2. **Axis Information**:
   - X-axis: label, units, range (min to max), scale type (linear/log)
   - Y-axis: label, units, range (min to max), scale type (linear/log)

3. **Data Series**: For each visible data series:
   - Name/label (from legend if available)
   - Marker style (circle, square, triangle, etc.)
   - Color
   - Extracted data points as (x, y) pairs

4. **Error Bars**: If present, estimate their values

5. **Fitted Curves**: If present, describe the apparent relationship

Return as JSON:
```json
{
  "graph_type": "scatter",
  "title": "graph title if visible",
  "x_axis": {
    "label": "Temperature",
    "units": "K",
    "range": [0, 1000],
    "scale": "linear"
  },
  "y_axis": {
    "label": "Conductivity",
    "units": "S/cm",
    "range": [0.01, 100],
    "scale": "log"
  },
  "data_series": [
    {
      "name": "Sample A",
      "marker": "circle",
      "color": "blue",
      "points": [[100, 0.5], [200, 1.2], [300, 2.8]],
      "error_bars": {
        "type": "symmetric",
        "values": [[0.1, 0.05], [0.15, 0.1], [0.2, 0.15]]
      }
    }
  ],
  "fitted_curves": [
    {
      "type": "linear",
      "equation": "y = 0.01x + 0.2",
      "r_squared": 0.95
    }
  ],
  "notes": "any additional observations"
}
```

Be conservative - only extract points you can clearly identify. If uncertain,
indicate approximate values or ranges."""

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
    text = response.content[0].text
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())

    return {"error": "Could not parse JSON", "raw": text}

# Example usage
result = extract_graph_with_llm("figure_3a.png")
print(json.dumps(result, indent=2))
```

### Verification Prompt

```python
def verify_extraction(image_path: str, extracted_data: dict) -> dict:
    """Verify extracted data against the source image."""

    client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    prompt = f"""I extracted the following data from this graph. Please verify:

Extracted data:
{json.dumps(extracted_data, indent=2)}

Check:
1. Are the axis ranges correct?
2. Do the extracted points visually match the graph?
3. Are there any obvious errors or missed points?
4. Do the values seem reasonable given the axis scales?

Provide corrections if needed, or confirm "VERIFIED" if accurate."""

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )

    return {"verification": response.content[0].text}
```

## Method 3: OpenCV Color Detection

For graphs with clear color-coded data series.

```python
import cv2
import numpy as np
import pandas as pd

def extract_by_color(image_path: str, color_hsv_range: tuple, axis_bounds: dict) -> list:
    """
    Extract data points by detecting a specific color.

    Args:
        image_path: Path to graph image
        color_hsv_range: ((h_min, s_min, v_min), (h_max, s_max, v_max))
        axis_bounds: {
            'x_pixel_range': (x_min_px, x_max_px),
            'y_pixel_range': (y_min_px, y_max_px),
            'x_data_range': (x_min, x_max),
            'y_data_range': (y_min, y_max)
        }

    Returns:
        List of (x, y) data points
    """
    # Load image
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Create mask for target color
    lower, upper = color_hsv_range
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

    # Find contours (data points)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get centroid of each contour
    pixel_points = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            pixel_points.append((cx, cy))

    # Convert to data coordinates
    def pixel_to_data(px, py):
        x_px_min, x_px_max = axis_bounds['x_pixel_range']
        y_px_min, y_px_max = axis_bounds['y_pixel_range']
        x_min, x_max = axis_bounds['x_data_range']
        y_min, y_max = axis_bounds['y_data_range']

        x = x_min + (px - x_px_min) / (x_px_max - x_px_min) * (x_max - x_min)
        # Y axis is inverted in images (0 at top)
        y = y_max - (py - y_px_min) / (y_px_max - y_px_min) * (y_max - y_min)
        return (round(x, 3), round(y, 3))

    data_points = [pixel_to_data(px, py) for px, py in pixel_points]

    # Sort by x coordinate
    data_points.sort(key=lambda p: p[0])

    return data_points

# Example: Extract blue data points
axis_bounds = {
    'x_pixel_range': (100, 600),   # Pixel coordinates of x-axis
    'y_pixel_range': (50, 450),    # Pixel coordinates of y-axis
    'x_data_range': (0, 100),      # Actual data range
    'y_data_range': (0, 10)        # Actual data range
}

# Blue color in HSV
blue_hsv = ((100, 50, 50), (130, 255, 255))

points = extract_by_color("graph.png", blue_hsv, axis_bounds)
print(f"Extracted {len(points)} points")

# Convert to DataFrame
df = pd.DataFrame(points, columns=['x', 'y'])
df.to_csv("extracted_data.csv", index=False)
```

### Common Color Ranges (HSV)

```python
COLOR_RANGES = {
    'red': ((0, 50, 50), (10, 255, 255)),      # Also check (170, 50, 50), (180, 255, 255)
    'blue': ((100, 50, 50), (130, 255, 255)),
    'green': ((40, 50, 50), (80, 255, 255)),
    'yellow': ((20, 50, 50), (40, 255, 255)),
    'cyan': ((80, 50, 50), (100, 255, 255)),
    'magenta': ((140, 50, 50), (170, 255, 255)),
    'orange': ((10, 50, 50), (25, 255, 255)),
    'black': ((0, 0, 0), (180, 255, 50)),
}
```

## Method 4: Interactive Python Digitization

```python
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Cursor
import json

class GraphDigitizer:
    """Interactive graph digitization tool."""

    def __init__(self, image_path: str):
        self.image_path = image_path
        self.calibration_points = []
        self.data_points = []
        self.calibrated = False

    def run(self):
        """Run interactive digitization."""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        img = mpimg.imread(self.image_path)
        self.ax.imshow(img)

        # Add cursor crosshairs
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)

        # Connect click event
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # Instructions
        self.ax.set_title(
            "CALIBRATION: Click 4 points - X_min, X_max, Y_min, Y_max\n"
            "(After calibration, click data points. Close window when done.)"
        )

        plt.show()
        return self.data_points

    def onclick(self, event):
        if event.inaxes != self.ax:
            return

        if not self.calibrated:
            # Calibration mode
            self.calibration_points.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'ro', markersize=10)
            self.fig.canvas.draw()

            labels = ['X_min', 'X_max', 'Y_min', 'Y_max']
            if len(self.calibration_points) <= 4:
                idx = len(self.calibration_points) - 1
                print(f"Marked {labels[idx]} at pixel ({event.xdata:.1f}, {event.ydata:.1f})")

            if len(self.calibration_points) == 4:
                self.get_calibration_values()
                self.calibrated = True
                self.ax.set_title("DATA: Click on data points. Close window when done.")
        else:
            # Data collection mode
            x_data, y_data = self.pixel_to_data(event.xdata, event.ydata)
            self.data_points.append((x_data, y_data))
            self.ax.plot(event.xdata, event.ydata, 'gx', markersize=8)
            self.fig.canvas.draw()
            print(f"Point {len(self.data_points)}: ({x_data:.4f}, {y_data:.4f})")

    def get_calibration_values(self):
        """Prompt user for calibration values."""
        print("\n--- Enter calibration values ---")
        self.x_min_val = float(input("X-axis minimum value: "))
        self.x_max_val = float(input("X-axis maximum value: "))
        self.y_min_val = float(input("Y-axis minimum value: "))
        self.y_max_val = float(input("Y-axis maximum value: "))

        # Store pixel positions
        self.x_min_px = self.calibration_points[0][0]
        self.x_max_px = self.calibration_points[1][0]
        self.y_min_px = self.calibration_points[2][1]
        self.y_max_px = self.calibration_points[3][1]

        print(f"\nCalibration complete:")
        print(f"  X: {self.x_min_val} to {self.x_max_val}")
        print(f"  Y: {self.y_min_val} to {self.y_max_val}")
        print("\nNow click on data points...")

    def pixel_to_data(self, px, py):
        """Convert pixel coordinates to data coordinates."""
        x = self.x_min_val + (px - self.x_min_px) / (self.x_max_px - self.x_min_px) * (self.x_max_val - self.x_min_val)
        y = self.y_max_val - (py - self.y_max_px) / (self.y_min_px - self.y_max_px) * (self.y_max_val - self.y_min_val)
        return (x, y)

    def save_data(self, output_path: str):
        """Save extracted data to file."""
        import pandas as pd

        df = pd.DataFrame(self.data_points, columns=['x', 'y'])
        df.to_csv(output_path, index=False)
        print(f"Saved {len(self.data_points)} points to {output_path}")

# Usage
digitizer = GraphDigitizer("figure.png")
points = digitizer.run()
digitizer.save_data("extracted_points.csv")
```

## Post-Processing Extracted Data

```python
import pandas as pd
import numpy as np
from scipy import interpolate

def process_extracted_data(points: list) -> pd.DataFrame:
    """Clean and process extracted data points."""

    df = pd.DataFrame(points, columns=['x', 'y'])

    # Sort by x
    df = df.sort_values('x').reset_index(drop=True)

    # Remove duplicates (keep mean y for same x)
    df = df.groupby('x', as_index=False).agg({'y': 'mean'})

    return df

def interpolate_data(df: pd.DataFrame, n_points: int = 100) -> pd.DataFrame:
    """Interpolate extracted data to regular grid."""

    x = df['x'].values
    y = df['y'].values

    # Create interpolation function
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')

    # New regular x grid
    x_new = np.linspace(x.min(), x.max(), n_points)
    y_new = f(x_new)

    return pd.DataFrame({'x': x_new, 'y': y_new})

def estimate_uncertainty(df: pd.DataFrame, source: str = 'llm') -> pd.DataFrame:
    """Add uncertainty estimates based on extraction method."""

    # Typical uncertainties by method
    uncertainties = {
        'webplotdigitizer': 0.01,  # ~1% for careful digitization
        'llm': 0.05,               # ~5% for LLM extraction
        'color_detection': 0.02,   # ~2% for automatic detection
    }

    rel_uncertainty = uncertainties.get(source, 0.05)

    df['y_error'] = abs(df['y']) * rel_uncertainty
    df['x_error'] = abs(df['x']) * rel_uncertainty

    return df
```

## Complete Workflow

```python
def digitize_graph_complete(
    image_path: str,
    output_path: str = None,
    method: str = 'llm'
) -> dict:
    """
    Complete graph digitization workflow.

    Args:
        image_path: Path to graph image
        output_path: Path for output CSV (optional)
        method: 'llm', 'interactive', or 'color'

    Returns:
        Dictionary with extracted data and metadata
    """
    result = {
        'source': image_path,
        'method': method,
        'data': None,
        'metadata': {}
    }

    if method == 'llm':
        extracted = extract_graph_with_llm(image_path)

        if 'error' not in extracted:
            result['metadata'] = {
                'x_axis': extracted.get('x_axis'),
                'y_axis': extracted.get('y_axis'),
                'graph_type': extracted.get('graph_type')
            }

            # Combine all series
            all_points = []
            for series in extracted.get('data_series', []):
                for point in series.get('points', []):
                    all_points.append({
                        'x': point[0],
                        'y': point[1],
                        'series': series.get('name', 'unknown')
                    })

            result['data'] = pd.DataFrame(all_points)

    elif method == 'interactive':
        digitizer = GraphDigitizer(image_path)
        points = digitizer.run()
        result['data'] = pd.DataFrame(points, columns=['x', 'y'])
        result['metadata'] = {
            'x_range': (digitizer.x_min_val, digitizer.x_max_val),
            'y_range': (digitizer.y_min_val, digitizer.y_max_val)
        }

    # Save output
    if output_path and result['data'] is not None:
        result['data'].to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

    return result

# Usage
result = digitize_graph_complete("figure_3a.png", "data.csv", method='llm')
print(f"Extracted {len(result['data'])} points")
```

## Validation Checklist

- [ ] Calibration points match known axis values
- [ ] Extracted range matches visible axis range
- [ ] Number of points seems reasonable for graph density
- [ ] No obvious outliers or impossible values
- [ ] Log scale handled correctly (if applicable)
- [ ] Error bars captured (if present)
- [ ] All data series extracted (if multiple)
