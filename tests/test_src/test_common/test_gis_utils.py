import unittest
from unittest.mock import MagicMock, patch

import geopandas as gpd
from shapely.geometry import LineString, MultiPolygon, Point, Polygon

from src.common.gis_utils import get_map_center_and_zoom, load_bridge_shapefile, prepare_bridge_data_for_viktor  # , load_bridge_shapefile


# Helper function to create a mock GeoDataFrame
def create_mock_gdf(rows_data, crs_string=None):
    mock_gdf = MagicMock(spec=gpd.GeoDataFrame)

    # Mock CRS
    if crs_string:
        mock_crs_obj = MagicMock(name="MockCRS")  # Give it a name for easier debugging
        mock_crs_obj.__str__.return_value = crs_string
        mock_crs_obj.to_string.return_value = crs_string

        # Define how the mock CRS object compares with other objects (especially strings)
        def mock_crs_eq(other_obj):
            return str(mock_crs_obj) == str(other_obj)

        def mock_crs_ne(other_obj):
            return str(mock_crs_obj) != str(other_obj)

        mock_crs_obj.__eq__ = MagicMock(side_effect=mock_crs_eq)
        mock_crs_obj.__ne__ = MagicMock(side_effect=mock_crs_ne)

        mock_gdf.crs = mock_crs_obj
    else:
        mock_gdf.crs = None

    mock_rows = []
    for data_dict in rows_data:
        mock_row = MagicMock()
        for key, value in data_dict.items():
            if key == "geometry":  # Special handling for geometry
                mock_geometry = MagicMock()
                if isinstance(value, Point):
                    mock_geometry.type = "Point"
                    mock_geometry.x = value.x
                    mock_geometry.y = value.y
                elif isinstance(value, Polygon):
                    mock_geometry.type = "Polygon"
                    mock_geometry.exterior = MagicMock()
                    mock_geometry.exterior.coords = list(value.exterior.coords)
                elif isinstance(value, LineString):
                    mock_geometry.type = "LineString"
                    mock_geometry.coords = list(value.coords)
                elif isinstance(value, MultiPolygon):
                    mock_geometry.type = "MultiPolygon"
                    # Ensure geoms is a list of mock polygons if needed, here we mock the first one
                    mock_first_polygon = MagicMock()
                    mock_first_polygon.exterior = MagicMock()
                    mock_first_polygon.exterior.coords = list(value.geoms[0].exterior.coords)
                    mock_geometry.geoms = [mock_first_polygon]
                else:  # For other types or None
                    mock_geometry.type = value.type if hasattr(value, "type") else "Unknown"

                setattr(mock_row, "geometry", mock_geometry)
            else:
                setattr(mock_row, key, value)

        # Make the mock_row behave like a dictionary for properties extraction
        def getitem_side_effect(key):
            if key == "geometry":
                raise KeyError("geometry should be excluded")
            return getattr(mock_row, key)

        mock_row.__getitem__.side_effect = getitem_side_effect
        mock_row.items.return_value = [(k, v) for k, v in data_dict.items() if k != "geometry"]  # for properties

        mock_rows.append(mock_row)

    mock_gdf.iterrows.return_value = iter([(idx, row) for idx, row in enumerate(mock_rows)])

    # Mock to_crs
    # By default, to_crs returns a new mock_gdf that is the same as the input for simplicity,
    # unless we want to specifically test the transformation.
    mock_gdf.to_crs.return_value = mock_gdf

    return mock_gdf


class TestGisUtilsPrepareBridgeData(unittest.TestCase):
    def test_empty_gdf(self):
        # Arrange
        mock_gdf = create_mock_gdf([], crs_string="EPSG:4326")
        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)
        # Assert
        self.assertEqual(result, [])
        mock_gdf.to_crs.assert_not_called()  # Should not be called if CRS is already correct

    def test_no_crs_on_gdf(self):
        # Arrange
        # Create a polygon for testing
        poly = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        rows_data = [{"id": 1, "name": "BridgeA", "geometry": poly}]
        mock_gdf_no_crs = create_mock_gdf(rows_data, crs_string=None)

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf_no_crs)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "polygon")
        mock_gdf_no_crs.to_crs.assert_not_called()  # Should not attempt conversion if gdf.crs is None

    def test_crs_conversion_needed(self):
        # Arrange
        poly = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])  # Dummy polygon
        rows_data = [{"id": 1, "name": "BridgeA", "geometry": poly}]
        mock_gdf_other_crs = create_mock_gdf(rows_data, crs_string="EPSG:28992")  # RD New

        # We need to_crs to return a GDF with the correct EPSG:4326 so the rest of the function proceeds
        mock_gdf_converted = create_mock_gdf(rows_data, crs_string="EPSG:4326")
        mock_gdf_other_crs.to_crs.return_value = mock_gdf_converted

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf_other_crs)

        # Assert
        mock_gdf_other_crs.to_crs.assert_called_once_with("EPSG:4326")
        self.assertEqual(len(result), 1)  # Ensure processing continues after mocked conversion
        self.assertEqual(result[0]["type"], "polygon")

    def test_point_geometry(self):
        # Arrange
        point = Point(5, 52)  # lon, lat for a Point
        rows_data = [{"id": "p1", "desc": "Test Point", "geometry": point}]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 1)
        feature = result[0]
        self.assertEqual(feature["type"], "point")
        self.assertEqual(feature["coordinates"], [(52, 5)])  # VIKTOR expects (lat, lon)
        self.assertEqual(feature["properties"]["id"], "p1")
        self.assertEqual(feature["properties"]["desc"], "Test Point")

    def test_polygon_geometry(self):
        # Arrange
        poly_coords_exterior = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]  # Closed exterior
        polygon = Polygon(poly_coords_exterior[:-1])  # Shapely Polygon doesn't need explicit closing for constructor

        rows_data = [{"id": "poly1", "geometry": polygon}]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 1)
        feature = result[0]
        self.assertEqual(feature["type"], "polygon")
        # VIKTOR expects (lat,lon) and closed polygon (first point repeated at end)
        expected_coords = [(y, x) for x, y in poly_coords_exterior]
        self.assertEqual(feature["coordinates"], expected_coords)
        self.assertEqual(feature["properties"]["id"], "poly1")

    def test_linestring_geometry(self):
        # Arrange
        line_coords = [(10, 20), (11, 21), (12, 22)]
        linestring = LineString(line_coords)
        rows_data = [{"id": "line1", "geometry": linestring}]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 1)
        feature = result[0]
        self.assertEqual(feature["type"], "linestring")
        expected_coords = [(y, x) for x, y in line_coords]
        self.assertEqual(feature["coordinates"], expected_coords)
        self.assertEqual(feature["properties"]["id"], "line1")

    def test_multipolygon_geometry(self):
        # Arrange
        poly1_coords = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        poly2_coords = [(2, 2), (2, 3), (3, 3), (3, 2), (2, 2)]
        multipolygon = MultiPolygon([Polygon(poly1_coords[:-1]), Polygon(poly2_coords[:-1])])
        rows_data = [{"id": "mp1", "geometry": multipolygon}]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 1)  # Should process the first polygon
        feature = result[0]
        self.assertEqual(feature["type"], "multipolygon")
        # Expects coords from the first polygon
        expected_coords = [(y, x) for x, y in poly1_coords]
        self.assertEqual(feature["coordinates"], expected_coords)
        self.assertEqual(feature["properties"]["id"], "mp1")

    def test_unsupported_geometry_type(self):
        # Arrange
        mock_unsupported_geom = MagicMock()
        mock_unsupported_geom.type = "GeometryCollection"  # Example of an unsupported type
        rows_data = [{"id": "unsupported1", "geometry": mock_unsupported_geom}]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 0)  # Should skip unsupported geometry

    def test_all_properties_converted_to_string(self):
        # Arrange
        point = Point(1, 2)
        rows_data = [{"id": 123, "value": 45.6, "active": True, "geometry": point}]  # Mixed types
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 1)
        properties = result[0]["properties"]
        self.assertEqual(properties["id"], "123")
        self.assertEqual(properties["value"], "45.6")
        self.assertEqual(properties["active"], "True")
        self.assertNotIn("geometry", properties)

    def test_multiple_features_mixed_types(self):
        # Arrange
        point = Point(1, 1)
        poly_coords = [(10, 10), (10, 11), (11, 11), (11, 10), (10, 10)]
        polygon = Polygon(poly_coords[:-1])

        rows_data = [
            {"name": "Feature1", "type_val": "P", "geometry": point},
            {"name": "Feature2", "type_val": "Poly", "geometry": polygon},
            {"name": "Feature3", "type_val": "Invalid", "geometry": MagicMock(type="SomethingElse")},
        ]
        mock_gdf = create_mock_gdf(rows_data, crs_string="EPSG:4326")

        # Act
        result = prepare_bridge_data_for_viktor(mock_gdf)

        # Assert
        self.assertEqual(len(result), 2)  # Skips the invalid geometry one
        self.assertEqual(result[0]["type"], "point")
        self.assertEqual(result[0]["properties"]["name"], "Feature1")
        self.assertEqual(result[1]["type"], "polygon")
        self.assertEqual(result[1]["properties"]["name"], "Feature2")


class TestGisUtilsGetMapCenterAndZoom(unittest.TestCase):
    def test_crs_conversion_for_get_center_zoom(self):
        # Arrange
        mock_gdf_other_crs = create_mock_gdf([], crs_string="EPSG:28992")
        # Mock total_bounds on the GDF that to_crs will return
        mock_gdf_converted = create_mock_gdf([], crs_string="EPSG:4326")
        mock_gdf_converted.total_bounds = [0.0, 0.0, 0.01, 0.01]  # minx, miny, maxx, maxy (small diff for specific zoom)
        mock_gdf_other_crs.to_crs.return_value = mock_gdf_converted

        # Act
        center, zoom = get_map_center_and_zoom(mock_gdf_other_crs)

        # Assert
        mock_gdf_other_crs.to_crs.assert_called_once_with("EPSG:4326")
        self.assertIsInstance(center, tuple)
        self.assertIsInstance(zoom, int)

    def test_no_crs_conversion_if_already_epsg4326(self):
        # Arrange
        mock_gdf = create_mock_gdf([], crs_string="EPSG:4326")
        mock_gdf.total_bounds = [4.0, 52.0, 4.01, 52.01]  # Example bounds

        # Act
        center, zoom = get_map_center_and_zoom(mock_gdf)

        # Assert
        mock_gdf.to_crs.assert_not_called()
        self.assertAlmostEqual(center[0], 52.005)  # lat
        self.assertAlmostEqual(center[1], 4.005)  # lon

    def test_center_calculation(self):
        # Arrange
        mock_gdf = create_mock_gdf([], crs_string="EPSG:4326")
        minx, miny, maxx, maxy = 4.8, 52.3, 5.0, 52.5
        mock_gdf.total_bounds = [minx, miny, maxx, maxy]
        expected_center_lat = (miny + maxy) / 2
        expected_center_lon = (minx + maxx) / 2

        # Act
        (center_lat, center_lon), zoom = get_map_center_and_zoom(mock_gdf)

        # Assert
        self.assertAlmostEqual(center_lat, expected_center_lat)
        self.assertAlmostEqual(center_lon, expected_center_lon)

    # Test cases for different zoom levels based on lon_diff
    def run_zoom_test(self, bounds, expected_zoom):
        # The mock_create_gdf_func_not_used argument is removed
        mock_gdf = create_mock_gdf([], crs_string="EPSG:4326")  # Directly call the helper
        mock_gdf.total_bounds = bounds
        _center, zoom = get_map_center_and_zoom(mock_gdf)
        self.assertEqual(zoom, expected_zoom)

    def test_zoom_level_greater_than_0_5(self):
        # lon_diff = 1.0 (maxx - minx)
        self.run_zoom_test(bounds=[0.0, 0.0, 1.0, 1.0], expected_zoom=10)

    def test_zoom_level_greater_than_0_1_less_than_0_5(self):
        # lon_diff = 0.2
        self.run_zoom_test(bounds=[0.0, 0.0, 0.2, 0.2], expected_zoom=11)

    def test_zoom_level_greater_than_0_05_less_than_0_1(self):
        # lon_diff = 0.07
        self.run_zoom_test(bounds=[0.0, 0.0, 0.07, 0.07], expected_zoom=12)

    def test_zoom_level_default_if_lon_diff_is_0_05(self):  # Edge case for default zoom
        # lon_diff = 0.05. According to current logic, 0.01 < lon_diff <= 0.05 maps to zoom 13.
        self.run_zoom_test(bounds=[0.0, 0.0, 0.05, 1.0], expected_zoom=13)

    def test_zoom_level_greater_than_0_01_less_than_0_05(self):
        # lon_diff = 0.02
        self.run_zoom_test(bounds=[0.0, 0.0, 0.02, 0.02], expected_zoom=13)

    def test_zoom_level_less_than_or_equal_0_01(self):
        # lon_diff = 0.005
        self.run_zoom_test(bounds=[0.0, 0.0, 0.005, 0.005], expected_zoom=14)
        # lon_diff = 0.01 (exact boundary)
        self.run_zoom_test(bounds=[0.0, 0.0, 0.01, 0.01], expected_zoom=14)


# We will add TestGisUtilsLoadBridgeShapefile later


class TestGisUtilsLoadBridgeShapefile(unittest.TestCase):
    @patch("src.common.gis_utils.gpd.read_file")
    def test_load_shapefile_no_filter(self, mock_gpd_read_file):
        # Arrange
        dummy_path = "/path/to/dummy.shp"
        mock_returned_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_gpd_read_file.return_value = mock_returned_gdf

        # Act
        result_gdf = load_bridge_shapefile(dummy_path)

        # Assert
        mock_gpd_read_file.assert_called_once_with(dummy_path)
        self.assertIs(result_gdf, mock_returned_gdf)

    @patch("src.common.gis_utils.gpd.read_file")
    def test_load_shapefile_with_single_filter(self, mock_gpd_read_file):
        # Arrange
        dummy_path = "/path/to/dummy.shp"
        filter_cond = {"MY_COLUMN": "MY_VALUE"}

        initial_mock_gdf = MagicMock(spec=gpd.GeoDataFrame, name="InitialGDF")
        mock_gpd_read_file.return_value = initial_mock_gdf

        mock_column_series = MagicMock(name="MockColumnSeries")
        mock_boolean_series = MagicMock(name="MockBooleanSeries")
        final_filtered_gdf = MagicMock(spec=gpd.GeoDataFrame, name="FinalFilteredGDF")

        # initial_mock_gdf["MY_COLUMN"] -> mock_column_series
        # mock_column_series == "MY_VALUE" -> mock_boolean_series
        # initial_mock_gdf[mock_boolean_series] -> final_filtered_gdf
        def getitem_side_effect_for_initial(key):
            if key == "MY_COLUMN":
                return mock_column_series
            if key is mock_boolean_series:  # Note: checking for specific mock object instance
                return final_filtered_gdf
            raise KeyError(f"Unexpected key for initial_mock_gdf: {key}")

        initial_mock_gdf.__getitem__ = MagicMock(side_effect=getitem_side_effect_for_initial)
        mock_column_series.__eq__ = MagicMock(return_value=mock_boolean_series)

        # Act
        result_gdf = load_bridge_shapefile(dummy_path, filter_condition=filter_cond)

        # Assert
        mock_gpd_read_file.assert_called_once_with(dummy_path)
        initial_mock_gdf.__getitem__.assert_any_call("MY_COLUMN")
        mock_column_series.__eq__.assert_called_once_with("MY_VALUE")
        initial_mock_gdf.__getitem__.assert_any_call(mock_boolean_series)
        self.assertIs(result_gdf, final_filtered_gdf)

    @patch("src.common.gis_utils.gpd.read_file")
    def test_load_shapefile_with_multiple_filters(self, mock_gpd_read_file):
        # Arrange
        dummy_path = "/path/to/dummy.shp"
        # Order of filters in dict might not be guaranteed, but the function iterates as is.
        # For stable test, use an ordered dict or rely on typical dict ordering for CPython 3.7+
        filter_cond = {"COL1": "VAL1", "COL2": 123}

        mock_gdf_initial = MagicMock(spec=gpd.GeoDataFrame, name="InitialGDF")
        mock_gdf_after_filter1 = MagicMock(spec=gpd.GeoDataFrame, name="GdfAfterFilter1")
        mock_gdf_after_filter2 = MagicMock(spec=gpd.GeoDataFrame, name="GdfAfterFilter2")  # This is the final one

        mock_gpd_read_file.return_value = mock_gdf_initial

        # Setup for COL1 -> VAL1 filter producing mock_gdf_after_filter1
        col1_series = MagicMock(name="Col1Series")
        bool_series1 = MagicMock(name="BoolSeries1")
        col1_series.__eq__ = MagicMock(return_value=bool_series1)

        def getitem_initial_gdf(key):
            if key == "COL1":
                return col1_series
            if key is bool_series1:
                return mock_gdf_after_filter1
            # If COL2 is accessed first (due to dict iteration order)
            if key == "COL2":
                # This case means COL2 was processed before COL1, so we need a series for it
                # and its __eq__ should produce a boolean mask, which then filters initial_mock_gdf
                # to produce an intermediate GDF (let's call it mock_gdf_temp_for_col2_first)
                # This highlights that testing arbitrary dict iteration order for chained mocks is complex.
                # For this test, we assume filter_cond.items() yields COL1 then COL2 or vice versa.
                # Let's assume COL1 is processed first as per dict insertion order in modern Python for this test.
                raise NotImplementedError("Dict iteration order caused COL2 to be processed first, mock needs adjustment")
            raise KeyError(f"Unexpected key for initial_mock_gdf: {key}")

        mock_gdf_initial.__getitem__ = MagicMock(side_effect=getitem_initial_gdf)

        # Setup for COL2 -> 123 filter (operates on mock_gdf_after_filter1) producing mock_gdf_after_filter2
        col2_series = MagicMock(name="Col2Series")
        bool_series2 = MagicMock(name="BoolSeries2")
        col2_series.__eq__ = MagicMock(return_value=bool_series2)

        def getitem_gdf_after_filter1(key):
            if key == "COL2":
                return col2_series
            if key is bool_series2:
                return mock_gdf_after_filter2
            # If COL1 was processed second
            if key == "COL1":
                raise NotImplementedError("Dict iteration order caused COL1 to be processed second, mock needs adjustment")
            raise KeyError(f"Unexpected key for mock_gdf_after_filter1: {key}")

        mock_gdf_after_filter1.__getitem__ = MagicMock(side_effect=getitem_gdf_after_filter1)

        # Act
        result_gdf = load_bridge_shapefile(dummy_path, filter_condition=filter_cond)

        # Assert
        mock_gpd_read_file.assert_called_once_with(dummy_path)

        # We assert based on the final result and that interactions happened.
        # The exact call order on __getitem__ for COL1 vs COL2 depends on dict iteration order.
        # We check that both columns were used for filtering.

        # Check that COL1 was used for filtering on initial_mock_gdf
        # (Could have been called with "COL1" or bool_series1)
        self.assertTrue(
            any(call_args[0] == "COL1" for call_args, _ in mock_gdf_initial.__getitem__.call_args_list)
            or any(call_args[0] is bool_series1 for call_args, _ in mock_gdf_initial.__getitem__.call_args_list)
        )
        if col1_series.method_calls:  # if COL1 was accessed
            col1_series.__eq__.assert_called_with("VAL1")

        # Check that COL2 was used for filtering on one of the GDFs
        col2_accessed_on_initial = any(call_args[0] == "COL2" for call_args, _ in mock_gdf_initial.__getitem__.call_args_list)
        col2_accessed_on_intermediate = any(call_args[0] == "COL2" for call_args, _ in mock_gdf_after_filter1.__getitem__.call_args_list)
        self.assertTrue(col2_accessed_on_initial or col2_accessed_on_intermediate)
        if col2_series.method_calls:  # if COL2 was accessed
            col2_series.__eq__.assert_called_with(123)

        self.assertIs(result_gdf, mock_gdf_after_filter2)  # This is the crucial check for the final output

    @patch("src.common.gis_utils.gpd.read_file")
    def test_load_shapefile_read_file_raises_exception(self, mock_gpd_read_file):
        # Arrange
        dummy_path = "/path/to/error.shp"
        mock_gpd_read_file.side_effect = OSError("File not found")

        # Act & Assert
        with self.assertRaisesRegex(IOError, "File not found"):
            load_bridge_shapefile(dummy_path)


if __name__ == "__main__":
    unittest.main()
