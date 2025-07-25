# F1 Data Visualization

This is a web application for visualizing and analyzing Formula 1 data.

## Overview

I built this web application to provide interactive visualizations and analysis of Formula 1 data, including telemetry, race analysis, and information about drivers, teams, and schedules.

## Features

- **Telemetry Visualization**: Compare speed traces, gear shifts, and track dominance between drivers.
- **Race Analysis**: Analyze race pace, team pace, and lap sections.
- **Information**: View driver standings, constructor standings, and race schedules.

## Project Structure

```
f1-web-app/
├── api/                  # Flask API
│   ├── routes/           # API endpoints
│   └── utils/            # API utilities
├── f1w-frontend/         # Next.js frontend
│   ├── app/              # Next.js app directory
│   │   ├── components/   # Reusable UI components
│   │   └── utils/        # Utility functions
│   └── ...               # Page components
├── docs/                 # Documentation
├── examples/             # Example scripts
├── models/               # Shared domain models
├── scripts/              # Utility scripts
├── services/             # Data processing services
└── utils/                # Shared utilities
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- pip
- npm or yarn

### Installation

1.  **Backend**:
    -   Clone the repository and navigate to the `f1w` directory.
    -   Create a virtual environment: `python -m venv .venv`
    -   Activate the virtual environment: `source .venv/bin/activate`
    -   Install the dependencies: `pip install -r requirements.txt`
2.  **Frontend**:
    -   Navigate to the `f1w-frontend` directory.
    -   Install the dependencies: `npm install`

### Running the Application

1.  **Backend**:
    -   Start the Flask server: `python f1w/run.py`
2.  **Frontend**:
    -   Start the Next.js development server: `cd f1w-frontend && npm run dev`

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1)
- [Flask](https://flask.palletsprojects.com/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)
- [D3.js](https://d3js.org/)
