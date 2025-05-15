"""Functions for geometry calculations in the Bridge application."""
import csv
import os
from pathlib import Path

def get_steel_qualities():
    """Get list of available steel qualities from the CSV file.
    
    Returns:
        list: List of steel quality names
    """
    csv_path = Path(__file__).parent.parent.parent / "resources" / "betonstaalkwaliteit.csv"
    steel_qualities = []
    
    with open(csv_path, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=';')
        for row in csv_reader:
            # The first column header is "Betonstaalkwaliteit"
            steel_qualities.append(row["Betonstaalkwaliteit"].strip('"'))
    
    return steel_qualities

def calculate_zone_number(array_index: int, **kwargs) -> str:
    """Calculate the zone number based on the array index.
    
    Args:
        array_index: The index in the array (0-based)
        **kwargs: Additional keyword arguments (not used but included for compatibility)
        
    Returns:
        str: Zone number in format "location-segment" where:
            - location (1-3): represents zone location (1=left, 2=middle, 3=right)
            - segment: represents the segment number (1-based)
    """
    location = (array_index % 3) + 1  # Cycles through 1,2,3 for zone location
    segment = (array_index // 3) + 1  # Increments segment number every 3 zones
    result = f"{location}-{segment}"
    return result
