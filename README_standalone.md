# F1 Telemetry Standalone Visualization

This tool provides a standalone HTML visualization for F1 telemetry data, specifically for Hamilton vs Verstappen at Bahrain 2023 Qualifying.

## Features

- **Speed Trace Visualization**: Compare speed and throttle data between drivers
- **Gear Shifts Visualization**: View gear shift patterns around the track for each driver
- **Track Dominance Visualization**: See which driver is fastest in each mini-sector
- **Adjustable Visualization Sizes**: Easily modify the height of each visualization

## Usage

1. Run the script to generate the visualization:
   ```
   cd f1w
   python standalone_telemetry.py
   ```

2. Open the generated HTML file in a web browser:
   ```
   # On Linux
   xdg-open standalone_telemetry.html
   
   # On macOS
   open standalone_telemetry.html
   
   # On Windows
   start standalone_telemetry.html
   ```

3. Use the height controls in each visualization card to adjust the size:
   - Enter a new height value in pixels
   - Click the "Apply" button to resize the visualization

## Customization

To modify the script for different drivers, races, or sessions:

1. Open `standalone_telemetry.py` in a text editor
2. Modify the constants at the top of the file:
   ```python
   YEAR = 2023
   RACE = "Bahrain"
   SESSION_TYPE = "Q"  # Qualifying
   DRIVER1 = "HAM"  # Hamilton
   DRIVER2 = "VER"  # Verstappen
   ```
3. Run the script again to generate a new visualization

## How It Works

The script uses FastF1 to load telemetry data directly from the cache, generates visualizations using matplotlib, and embeds them as base64-encoded images in a standalone HTML file. This approach eliminates the need for a web server and allows for easy sharing and viewing of the visualizations.

## Requirements

- Python 3.8+
- FastF1
- Matplotlib
- NumPy
- Pandas

## Notes on Mini-Sectors

The track dominance visualization divides the track into mini-sectors (default: 20) and colors each sector according to which driver was fastest in that section. This provides a visual representation of where each driver has an advantage on the track.

Mini-sectors can be created based on:
- Distance (default): Divides the track into equal distance segments
- Time: Divides the lap into equal time segments
- Angle: Creates more natural segments around corners

To modify the number or type of mini-sectors, adjust the parameters in the `create_track_dominance_plot` method.
