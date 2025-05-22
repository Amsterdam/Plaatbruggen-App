"""Functions for geometry calculations in the Bridge application."""
import csv
import os
from pathlib import Path
from app.constants import REINFORCEMENT_PATH

def get_steel_qualities():
    """Get list of available steel qualities from the CSV file.
    
    Returns:
        list: List of steel quality names
    """
    csv_path = REINFORCEMENT_PATH
    steel_qualities = []
    
    with open(csv_path, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=';')
        for row in csv_reader:
            # The first column header is "Betonstaalkwaliteit"
            steel_qualities.append(row["Betonstaalkwaliteit"].strip('"'))
    
    return steel_qualities

