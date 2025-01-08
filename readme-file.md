# Naoris Protocol Marketing Dashboard

A Streamlit-based dashboard for visualizing token unlocks and supply metrics for the Naoris Protocol project.

## Project Structure

```
project_folder/
├── app/
│   ├── main.py                # Main Streamlit application
│   ├── components/
│   │   ├── charts.py         # Visualization components
│   │   └── widgets.py        # UI widget components
│   ├── utils/
│   │   ├── data.py          # Data loading and processing
│   │   └── helpers.py       # Helper functions
│   └── config/
│       └── settings.py       # App settings
├── data/
│   ├── Database.json        # Token distribution data
│   └── streamlit_emissions.json  # Emissions schedule
└── assets/
    ├── logo.png            # Project logo
    └── blacktokenomics.png # Company logo
```

## Features

- Interactive supply shock visualization
- Token unlock schedule tracking
- Customizable selling pressure assumptions
- Real-time value calculations
- Investor metrics tracking

## Setup & Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd naoris_marketing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app/main.py
```

## Usage

1. **Selling Pressure Settings**
   - Adjust the selling pressure percentage (0-100%)
   - Choose selling pressure source (Unlocks/Circulation)

2. **Temporary Settings**
   - Set expected FDV at launch
   - Select month to view specific unlock metrics

3. **Visualization**
   - View monthly supply shock scale
   - Track unlock values and investor metrics
   - Monitor token distribution

## File Descriptions

- `main.py`: Entry point of the application, handles UI layout and data flow
- `charts.py`: Contains functions for creating supply shock and emissions charts
- `widgets.py`: Custom UI components for metric displays
- `data.py`: Data loading and processing utilities
- `helpers.py`: Helper functions for formatting and calculations
- `settings.py`: Application-wide configuration

## Data Files

1. **Database.json**
   - Token distribution data
   - Vesting schedules
   - Allocation details

2. **streamlit_emissions.json**
   - Monthly emissions schedule
   - Token unlock data
   - Distribution timing

## Key Components

1. **Supply Shock Calculation**
   - Tracks monthly token releases
   - Calculates impact on token supply
   - Visualizes supply shock metrics

2. **Value Metrics**
   - Unlock value calculations
   - Investor portion tracking
   - Future value projections

3. **UI Components**
   - Interactive sliders
   - Dynamic metric displays
   - Responsive charts

## Configuration

Adjust these settings in `config/settings.py`:
- Default selling pressure values
- UI color schemes
- Chart configurations
- Data processing parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- Other dependencies in requirements.txt