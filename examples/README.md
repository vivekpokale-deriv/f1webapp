# F1 Web App Examples

This directory contains example scripts that demonstrate how to use various features of the F1 Web App.

## Mini-Sectors Example

The `minisectors_example.py` script demonstrates how to use the mini-sectors feature to analyze which driver is fastest in different parts of a track.

### Running the Example

To run the mini-sectors example:

```bash
cd f1-web-app
python examples/minisectors_example.py
```

This will:
1. Load the 2023 Monaco Grand Prix qualifying session
2. Create mini-sectors using three different methods (distance, time, and angle)
3. Find the fastest driver in each mini-sector
4. Generate visualizations for each method

### Output

The script will generate three PNG files:
- `track_dominance_distance.png` - Mini-sectors based on equal distance segments
- `track_dominance_time.png` - Mini-sectors based on equal time segments
- `track_dominance_angle.png` - Mini-sectors based on track direction changes

### Customizing the Example

You can modify the example to use different:
- Sessions (year, race, session type)
- Number of mini-sectors
- Visualization styles

## Understanding the Code

The example demonstrates:

1. How to load a session using FastF1
2. How to get telemetry data for multiple drivers
3. How to create mini-sectors using the `MiniSectorAnalyzer` class
4. How to find the fastest driver in each mini-sector
5. How to visualize the results on a track map

For more details on mini-sectors, see the [mini-sectors documentation](../docs/minisectors.md).
