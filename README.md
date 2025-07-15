# F1 Web App

A web application for Formula 1 data visualization and analysis.

## Overview

This web application provides interactive visualizations and analysis of Formula 1 data, including telemetry, race analysis, and information about drivers, teams, and schedules.

## Features

- **Telemetry Visualization**: Compare speed traces, gear shifts, and track dominance between drivers
- **Race Analysis**: Analyze race pace, team pace, and lap sections
- **Information**: View driver standings, constructor standings, and race schedules

## Project Structure

```
f1-web-app/
├── api/                  # Flask API
│   ├── routes/           # API endpoints
│   └── utils/            # API utilities
├── docs/                 # Documentation
├── examples/             # Example scripts
├── models/               # Shared domain models
├── scripts/              # Utility scripts
├── services/             # Data processing services
├── static/               # Static files for web app
│   └── js/               # JavaScript files
├── templates/            # Templates for web app
└── utils/                # Shared utilities
```

## Getting Started

### Prerequisites

- Python 3.8+ (Python 3.12 compatibility notes below)
- pip

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd f1-web-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask server:
   ```
   python run.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000/health
   ```

## API Documentation

### Telemetry Endpoints

- `GET /api/telemetry/speed-trace/<year>/<race>/<session>/<driver1>/<driver2>`: Get speed trace comparison data
- `GET /api/telemetry/gear-shifts/<year>/<race>/<session>/<driver>`: Get gear shift data
- `GET /api/telemetry/track-dominance/<year>/<race>/<session>?drivers=<driver1>,<driver2>,...`: Get track dominance data

### Race Analysis Endpoints

- `GET /api/race-analysis/race-pace/<year>/<race>?drivers=<num_drivers>`: Get race pace comparison data
- `GET /api/race-analysis/team-pace/<year>/<race>`: Get team pace comparison data
- `GET /api/race-analysis/lap-sections/<year>/<race>/<session>?drivers=<driver1>,<driver2>,...`: Get lap sections analysis data

### Information Endpoints

- `GET /api/info/drivers?year=<year>`: Get driver standings
- `GET /api/info/constructors?year=<year>`: Get constructor standings
- `GET /api/info/next-event`: Get the next upcoming F1 event
- `GET /api/info/schedule?year=<year>`: Get the F1 schedule

## Python 3.12 Compatibility

Python 3.12 has removed the `distutils` module from the standard library, which can cause compatibility issues with some packages. We've taken steps to ensure compatibility:

1. Updated `requirements.txt` with packages that work with Python 3.12
2. Added modern packaging dependencies that don't rely on `distutils`
3. Provided a utility script to check for `distutils` warnings

### Checking for Distutils Issues

We've included a script to help identify any remaining `distutils` issues:

```bash
# Run the script to check for distutils warnings
python scripts/check_distutils_warnings.py
```

See the [scripts README](scripts/README.md) for more details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) for providing access to Formula 1 data
- [Flask](https://flask.palletsprojects.com/) for the web framework
