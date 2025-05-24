"""
Module for calculating psi factors for bridge load combinations.

This module provides functionality to calculate psi factors based on bridge span length
and reference period using bilinear interpolation. The psi factors are used in load
combinations for bridge design and assessment according to Dutch standards.

The module includes a predefined lookup table of psi factors for various span lengths
and reference periods, and provides interpolation for intermediate values. For span
lengths outside the valid range (20-200m), the values are clamped to the nearest
valid value.
"""

import numpy as np
from scipy.interpolate import RegularGridInterpolator  # type: ignore[import-untyped]

""""tedstandard: psi_factor.py"""

# Define constant lookup table at module level
PSI_FACTORS: dict[float, dict[int, float]] = {
    100: {20: 1.00, 50: 1.00, 100: 1.00, 200: 1.00},
    50: {20: 0.99, 50: 0.99, 100: 0.99, 200: 0.99},
    30: {20: 0.99, 50: 0.99, 100: 0.98, 200: 0.97},
    15: {20: 0.98, 50: 0.98, 100: 0.96, 200: 0.96},
    1: {20: 0.95, 50: 0.94, 100: 0.89, 200: 0.88},
    1 / 12: {20: 0.91, 50: 0.91, 100: 0.81, 200: 0.81},
}


def _clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamps a value between min and max values.

    Args:
        value: The value to clamp
        min_value: The minimum allowed value
        max_value: The maximum allowed value

    Returns:
        The clamped value

    """
    return max(min_value, min(value, max_value))


def validate_input(span: float, reference_period: float) -> tuple[float, float]:
    """
    Validate input parameters for psi factor calculation and clamp span between 20 and 200.

    Args:
        span: Bridge span length in meters
        reference_period: Reference period in years

    Returns:
        Tuple of (clamped_span, reference_period)

    Raises:
        TypeError: If inputs are not numeric values
        ValueError: If inputs are invalid values

    """
    if not isinstance(span, int | float) or not isinstance(reference_period, int | float):
        raise TypeError("Span and reference period must be numeric values")

    if span <= 0:
        raise ValueError("Span must be positive")
    if reference_period <= 0:
        raise ValueError("Reference period must be positive")

    valid_periods = sorted(PSI_FACTORS.keys())

    if reference_period > max(valid_periods):
        raise ValueError(f"Reference period must not exceed {max(valid_periods)} years")

    # Clamp span between 20 and 200 meters
    clamped_span = _clamp(span, 20, 200)

    return clamped_span, reference_period


def get_interpolation_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data for 2D interpolation from PSI_FACTORS table.

    Returns:
        Tuple containing span values, period values, and psi values as 2D array

    """
    spans = sorted(PSI_FACTORS[100].keys())
    periods = sorted(PSI_FACTORS.keys(), reverse=True)  # Sort periods in descending order

    values = np.zeros((len(periods), len(spans)))
    for i, period in enumerate(periods):
        for j, span in enumerate(spans):
            values[i, j] = PSI_FACTORS[period][span]

    return np.array(spans), np.array(periods), values


def get_psi_factor(span: float, reference_period: float) -> float:
    """
    Calculate psi factor using bilinear interpolation.

    Args:
        span: Bridge span length in meters (will be clamped between 20 and 200)
        reference_period: Reference period in years

    Returns:
        Interpolated psi factor value

    Raises:
        ValueError: If inputs are invalid or interpolation fails

    """
    clamped_span, ref_period = validate_input(span, reference_period)

    spans, periods, values = get_interpolation_data()
    interpolator = RegularGridInterpolator((periods, spans), values, method="linear", bounds_error=False, fill_value=None)

    result = interpolator(np.array([ref_period, clamped_span]))

    if result is None or np.isnan(result[0]):
        raise ValueError("Interpolation failed. Input values may be outside valid range.")

    return float(result[0])
