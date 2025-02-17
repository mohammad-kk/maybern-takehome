# Waterfall Distribution Engine

This application calculates the waterfall distribution of investment returns between Limited Partners (LPs) and General Partners (GPs) based on a 4-tier waterfall structure.

## Features

- 4-tier waterfall calculation:
  1. Return of Capital
  2. Preferred Return (8% hurdle)
  3. Catch-up (100%)
  4. Final Split (80/20)
- Handles multiple contributions and distributions
- Supports multiple investors
- Includes validation and error checking

## Requirements

- Python 3.8+
- pandas
- pytest (for running tests)

## Installation

1. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2.Install required packages:
pip install -r requirements.txt

3.Input Files
Place your input files in the src/data/ directory:
  waterfall_data - commitments.csv: Contains investor commitment details
  waterfall_data - transactions.csv: Contains contribution and distribution records

4.To Run:

python src/main.py
