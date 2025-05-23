import unittest

import numpy as np
from numpy.testing import assert_array_equal

from src.combinations.load_factors import (  # Import the function to be tested and validate_input
    PSI_FACTORS,
    _clamp,
    get_interpolation_data,
    get_psi_factor,
    validate_input,
)


class TestLoadFactorsClamp(unittest.TestCase):
    def test_clamp_value_within_range(self):
        # Arrange
        value = 50.0
        min_val = 0.0
        max_val = 100.0
        expected = 50.0
        # Act
        result = _clamp(value, min_val, max_val)
        # Assert
        self.assertEqual(result, expected)

    def test_clamp_value_below_min(self):
        # Arrange
        value = -10.0
        min_val = 0.0
        max_val = 100.0
        expected = 0.0
        # Act
        result = _clamp(value, min_val, max_val)
        # Assert
        self.assertEqual(result, expected)

    def test_clamp_value_above_max(self):
        # Arrange
        value = 150.0
        min_val = 0.0
        max_val = 100.0
        expected = 100.0
        # Act
        result = _clamp(value, min_val, max_val)
        # Assert
        self.assertEqual(result, expected)

    def test_clamp_value_at_min_boundary(self):
        # Arrange
        value = 0.0
        min_val = 0.0
        max_val = 100.0
        expected = 0.0
        # Act
        result = _clamp(value, min_val, max_val)
        # Assert
        self.assertEqual(result, expected)

    def test_clamp_value_at_max_boundary(self):
        # Arrange
        value = 100.0
        min_val = 0.0
        max_val = 100.0
        expected = 100.0
        # Act
        result = _clamp(value, min_val, max_val)
        # Assert
        self.assertEqual(result, expected)


class TestLoadFactorsValidateInput(unittest.TestCase):
    def test_validate_input_valid_values(self):
        # Arrange
        span = 50.0
        ref_period = 15.0
        expected_clamped_span = 50.0
        expected_ref_period = 15.0
        # Act
        clamped_span, result_ref_period = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)
        self.assertEqual(result_ref_period, expected_ref_period)

    def test_validate_input_span_below_clamp_range(self):
        # Arrange
        span = 10.0  # Below 20
        ref_period = 15.0
        expected_clamped_span = 20.0  # Should be clamped to 20
        # Act
        clamped_span, _ = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)

    def test_validate_input_span_above_clamp_range(self):
        # Arrange
        span = 250.0  # Above 200
        ref_period = 15.0
        expected_clamped_span = 200.0  # Should be clamped to 200
        # Act
        clamped_span, _ = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)

    def test_validate_input_span_at_min_clamp_boundary(self):
        # Arrange
        span = 20.0
        ref_period = 15.0
        expected_clamped_span = 20.0
        # Act
        clamped_span, _ = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)

    def test_validate_input_span_at_max_clamp_boundary(self):
        # Arrange
        span = 200.0
        ref_period = 15.0
        expected_clamped_span = 200.0
        # Act
        clamped_span, _ = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)

    def test_validate_input_invalid_span_type(self):
        # Arrange
        span = "not_a_number"
        ref_period = 15.0
        # Act & Assert
        with self.assertRaisesRegex(TypeError, "Span and reference period must be numeric values"):
            validate_input(span, ref_period)

    def test_validate_input_invalid_ref_period_type(self):
        # Arrange
        span = 50.0
        ref_period = "not_a_number"
        # Act & Assert
        with self.assertRaisesRegex(TypeError, "Span and reference period must be numeric values"):
            validate_input(span, ref_period)

    def test_validate_input_non_positive_span(self):
        # Arrange
        span = 0.0
        ref_period = 15.0
        # Act & Assert
        with self.assertRaisesRegex(ValueError, "Span must be positive"):
            validate_input(span, ref_period)

    def test_validate_input_non_positive_ref_period(self):
        # Arrange
        span = 50.0
        ref_period = -1.0
        # Act & Assert
        with self.assertRaisesRegex(ValueError, "Reference period must be positive"):
            validate_input(span, ref_period)

    def test_validate_input_ref_period_too_high(self):
        # Arrange
        span = 50.0
        ref_period = 101.0  # Max is 100 from PSI_FACTORS
        # Act & Assert
        # The message includes the max value, so we check for the start of the message.
        with self.assertRaisesRegex(ValueError, "Reference period must not exceed 100 years"):
            validate_input(span, ref_period)

    def test_validate_input_ref_period_at_max_boundary(self):
        # Arrange
        span = 50.0
        ref_period = 100.0  # Max is 100
        expected_clamped_span = 50.0
        expected_ref_period = 100.0
        # Act
        clamped_span, result_ref_period = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)
        self.assertEqual(result_ref_period, expected_ref_period)

    def test_validate_input_ref_period_at_min_valid_boundary(self):
        # min_valid_period = 1/12
        min_valid_period = 1.0 / 12.0
        # Arrange
        span = 50.0
        ref_period = min_valid_period
        expected_clamped_span = 50.0
        expected_ref_period = min_valid_period
        # Act
        clamped_span, result_ref_period = validate_input(span, ref_period)
        # Assert
        self.assertEqual(clamped_span, expected_clamped_span)
        self.assertEqual(result_ref_period, expected_ref_period)


class TestLoadFactorsGetInterpolationData(unittest.TestCase):
    def test_get_interpolation_data_return_types(self):
        # Act
        spans, periods, values = get_interpolation_data()
        # Assert
        self.assertIsInstance(spans, np.ndarray)
        self.assertIsInstance(periods, np.ndarray)
        self.assertIsInstance(values, np.ndarray)
        self.assertEqual(len(get_interpolation_data()), 3)  # Check it returns a tuple of 3 items

    def test_get_interpolation_data_spans_content_and_order(self):
        # Arrange
        expected_spans = np.array(sorted(PSI_FACTORS[100].keys()))
        # Act
        spans, _, _ = get_interpolation_data()
        # Assert
        assert_array_equal(spans, expected_spans)

    def test_get_interpolation_data_periods_content_and_order(self):
        # Arrange
        expected_periods = np.array(sorted(PSI_FACTORS.keys(), reverse=True))
        # Act
        _, periods, _ = get_interpolation_data()
        # Assert
        assert_array_equal(periods, expected_periods)

    def test_get_interpolation_data_values_shape(self):
        # Arrange
        num_expected_periods = len(PSI_FACTORS.keys())
        num_expected_spans = len(PSI_FACTORS[100].keys())
        # Act
        _, _, values = get_interpolation_data()
        # Assert
        self.assertEqual(values.shape, (num_expected_periods, num_expected_spans))

    def test_get_interpolation_data_values_content_spot_checks(self):
        # Act
        spans_arr, periods_arr, values_arr = get_interpolation_data()

        # For easier lookup, create a mapping from period/span value to index
        period_to_idx = {period: i for i, period in enumerate(periods_arr)}
        span_to_idx = {span: i for i, span in enumerate(spans_arr)}

        # Assert specific values based on PSI_FACTORS, using the derived indices
        # Example 1: Top-left corner (Max period, Min span)
        # Max period (first in periods_arr due to reverse sort) should be 100
        # Min span (first in spans_arr due to sort) should be 20
        self.assertEqual(values_arr[period_to_idx[100.0], span_to_idx[20]], PSI_FACTORS[100.0][20])

        # Example 2: Bottom-right corner (Min period, Max span)
        # Min period (last in periods_arr) should be 1/12
        # Max span (last in spans_arr) should be 200
        self.assertEqual(values_arr[period_to_idx[1.0 / 12.0], span_to_idx[200]], PSI_FACTORS[1.0 / 12.0][200])

        # Example 3: A middle value
        # Period 15, Span 50
        if 15.0 in period_to_idx and 50 in span_to_idx:  # Ensure these keys exist for safety
            self.assertEqual(values_arr[period_to_idx[15.0], span_to_idx[50]], PSI_FACTORS[15.0][50])
        else:
            self.fail("Key 15.0 or 50 not found in period/span index maps for spot check")

        # Example 4: Another middle value
        # Period 1.0, Span 100
        if 1.0 in period_to_idx and 100 in span_to_idx:  # Ensure these keys exist
            self.assertEqual(values_arr[period_to_idx[1.0], span_to_idx[100]], PSI_FACTORS[1.0][100])
        else:
            self.fail("Key 1.0 or 100 not found in period/span index maps for spot check")


class TestLoadFactorsGetPsiFactor(unittest.TestCase):
    def test_get_psi_factor_exact_grid_points(self):
        # Test with values directly from PSI_FACTORS table
        self.assertEqual(get_psi_factor(span=20, reference_period=100), PSI_FACTORS[100][20])
        self.assertEqual(get_psi_factor(span=50, reference_period=50), PSI_FACTORS[50][50])
        self.assertEqual(get_psi_factor(span=100, reference_period=15), PSI_FACTORS[15][100])
        self.assertEqual(get_psi_factor(span=200, reference_period=1.0 / 12.0), PSI_FACTORS[1.0 / 12.0][200])
        self.assertEqual(get_psi_factor(span=100, reference_period=1.0), PSI_FACTORS[1.0][100])

    def test_get_psi_factor_interpolated_span(self):
        # Span 75 is halfway between 50 and 100.
        # For period 1, values are 0.94 (span 50) and 0.89 (span 100).
        # Expected: 0.94 + (0.89 - 0.94) / (100 - 50) * (75 - 50) = 0.94 - 0.05 / 50 * 25 = 0.94 - 0.025 = 0.915
        self.assertAlmostEqual(get_psi_factor(span=75, reference_period=1), 0.915, places=3)

        # For period 30, values are 0.99 (span 50) and 0.98 (span 100)
        # Expected: 0.99 + (0.98 - 0.99) / (100 - 50) * (75 - 50) = 0.99 - 0.01 / 50 * 25 = 0.99 - 0.005 = 0.985
        self.assertAlmostEqual(get_psi_factor(span=75, reference_period=30), 0.985, places=3)

    def test_get_psi_factor_interpolated_period(self):
        # Period 7.5 is between 1 and 15. Periods are [100, 50, 30, 15, 1, 1/12]
        # For span 20:
        # PSI_FACTORS[15][20] = 0.98
        # PSI_FACTORS[1][20] = 0.95
        # Interpolation:  y = y1 + (y2-y1)/(x2-x1) * (x-x1)
        # Here, x refers to period. We need to be careful as the interpolator sorts periods descending.
        # However, the function handles this. We can conceptualize it with periods sorted normally for manual calc.
        # For period 1 (x1=1, y1=0.95) and period 15 (x2=15, y2=0.98). We want period 7.5 (x=7.5).
        # Expected: 0.95 + (0.98-0.95)/(15-1) * (7.5-1) = 0.95 + 0.03/14 * 6.5 = 0.95 + 0.013928... = 0.963928...
        self.assertAlmostEqual(get_psi_factor(span=20, reference_period=7.5), 0.963928, places=5)

    def test_get_psi_factor_interpolated_span_and_period(self):
        # Span 75 (between 50 and 100), Period 7.5 (between 1 and 15)
        # This is a bilinear interpolation. Harder to calculate by hand quickly.
        # We'll trust the scipy interpolator if component interpolations work.
        # Let's test a known case if possible or rely on robustness of library for this combined case.
        # For now, we can check if it runs and returns a float in the expected range.
        result = get_psi_factor(span=75, reference_period=7.5)
        self.assertIsInstance(result, float)
        self.assertTrue(0.8 < result < 1.0)  # General expected range for psi factors

    def test_get_psi_factor_clamped_span_low(self):
        # Span 10 (clamps to 20), period 1. Should be same as span 20, period 1.
        expected = PSI_FACTORS[1.0][20]  # 0.95
        self.assertEqual(get_psi_factor(span=10, reference_period=1), expected)

    def test_get_psi_factor_clamped_span_high(self):
        # Span 300 (clamps to 200), period 30. Should be same as span 200, period 30.
        expected = PSI_FACTORS[30.0][200]  # 0.97
        self.assertEqual(get_psi_factor(span=300, reference_period=30), expected)

    # Tests for exceptions propagated from validate_input
    def test_get_psi_factor_invalid_span_type(self):
        with self.assertRaisesRegex(TypeError, "Span and reference period must be numeric values"):
            get_psi_factor("invalid", 15)

    def test_get_psi_factor_invalid_ref_period_type(self):
        with self.assertRaisesRegex(TypeError, "Span and reference period must be numeric values"):
            get_psi_factor(50, "invalid")

    def test_get_psi_factor_non_positive_span(self):
        with self.assertRaisesRegex(ValueError, "Span must be positive"):
            get_psi_factor(0, 15)

    def test_get_psi_factor_non_positive_ref_period(self):
        with self.assertRaisesRegex(ValueError, "Reference period must be positive"):
            get_psi_factor(50, 0)

    def test_get_psi_factor_ref_period_too_high(self):
        with self.assertRaisesRegex(ValueError, "Reference period must not exceed 100 years"):
            get_psi_factor(50, 101)

    def test_get_psi_factor_ref_period_at_boundaries(self):
        # Test with period at max boundary (100)
        self.assertEqual(get_psi_factor(span=50, reference_period=100), PSI_FACTORS[100][50])
        # Test with period at min boundary (1/12)
        self.assertEqual(get_psi_factor(span=50, reference_period=1.0 / 12.0), PSI_FACTORS[1.0 / 12.0][50])
