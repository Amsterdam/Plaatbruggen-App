import unittest
import plotly.graph_objects as go
from src.common.plot_utils import create_text_annotations_from_data, create_structural_polygons_traces, create_bridge_outline_traces

class TestPlotUtilsCreateTextAnnotations(unittest.TestCase):

    def test_empty_label_data(self):
        # Arrange
        label_data = []
        # Act
        annotations = create_text_annotations_from_data(label_data)
        # Assert
        self.assertEqual(len(annotations), 0)
        self.assertIsInstance(annotations, list)

    def test_single_annotation_defaults(self):
        # Arrange
        label_data = [{"text": "Test1", "x": 10, "y": 20}]
        # Act
        annotations = create_text_annotations_from_data(label_data)
        # Assert
        self.assertEqual(len(annotations), 1)
        ann = annotations[0]
        self.assertIsInstance(ann, go.layout.Annotation)
        self.assertEqual(ann.text, "<b>Test1</b>")
        self.assertEqual(ann.x, 10)
        self.assertEqual(ann.y, 20)
        self.assertEqual(ann.font.size, 12)
        self.assertEqual(ann.font.color, "black")
        self.assertEqual(ann.xanchor, "center")
        self.assertEqual(ann.yanchor, "bottom")
        self.assertEqual(ann.showarrow, False)

    def test_multiple_annotations(self):
        # Arrange
        label_data = [
            {"text": "TestA", "x": 1, "y": 2},
            {"text": "TestB", "x": 3, "y": 4},
        ]
        # Act
        annotations = create_text_annotations_from_data(label_data)
        # Assert
        self.assertEqual(len(annotations), 2)
        self.assertEqual(annotations[0].text, "<b>TestA</b>")
        self.assertEqual(annotations[0].x, 1)
        self.assertEqual(annotations[1].text, "<b>TestB</b>")
        self.assertEqual(annotations[1].y, 4)

    def test_overridden_optional_arguments(self):
        # Arrange
        label_data = [{"text": "Override", "x": 5, "y": 15}]
        font_size = 16
        font_color = "red"
        xanchor = "left"
        yanchor = "top"
        showarrow = True
        text_prefix = "<i>"
        text_suffix = "</i>"
        # Act
        annotations = create_text_annotations_from_data(
            label_data,
            font_size=font_size,
            font_color=font_color,
            xanchor=xanchor,
            yanchor=yanchor,
            showarrow=showarrow,
            text_prefix=text_prefix,
            text_suffix=text_suffix,
        )
        # Assert
        self.assertEqual(len(annotations), 1)
        ann = annotations[0]
        self.assertEqual(ann.text, "<i>Override</i>")
        self.assertEqual(ann.font.size, font_size)
        self.assertEqual(ann.font.color, font_color)
        self.assertEqual(ann.xanchor, xanchor)
        self.assertEqual(ann.yanchor, yanchor)
        self.assertEqual(ann.showarrow, showarrow)

    def test_kwargs_passthrough(self):
        # Arrange
        label_data = [{"text": "Kwargs", "x": 1, "y": 1}]
        extra_kwargs = {"bgcolor": "blue", "borderpad": 4, "opacity": 0.7}
        # Act
        annotations = create_text_annotations_from_data(label_data, **extra_kwargs)
        # Assert
        self.assertEqual(len(annotations), 1)
        ann = annotations[0]
        self.assertEqual(ann.bgcolor, "blue")
        self.assertEqual(ann.borderpad, 4)
        self.assertEqual(ann.opacity, 0.7)
        self.assertEqual(ann.font.size, 12)
        self.assertEqual(ann.font.color, "black")

    def test_mixed_default_and_overridden_kwargs(self):
        # Arrange
        label_data = [{"text": "Mixed", "x": 0, "y": 0}]
        # Override one default, pass one kwarg
        # Act
        annotations = create_text_annotations_from_data(label_data, font_size=20, arrowwidth=2)
        # Assert
        ann = annotations[0]
        self.assertEqual(ann.font.size, 20) # Overridden
        self.assertEqual(ann.font.color, "black") # Default
        self.assertEqual(ann.arrowwidth, 2) # Kwarg
        self.assertEqual(ann.xanchor, "center") # Default

class TestPlotUtilsCreateStructuralPolygonsTraces(unittest.TestCase):

    def test_empty_polygons_data(self):
        # Arrange
        zone_polygons_data = []
        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)
        # Assert
        self.assertEqual(len(traces), 0)
        self.assertIsInstance(traces, list)

    def test_polygon_no_vertices_key(self):
        # Arrange
        zone_polygons_data = [{ "color": "blue" }] # No 'vertices' key
        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)
        # Assert
        self.assertEqual(len(traces), 0)

    def test_polygon_empty_vertices_list(self):
        # Arrange
        zone_polygons_data = [{ "vertices": [] }]
        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)
        # Assert
        self.assertEqual(len(traces), 0)

    def test_polygon_insufficient_vertices(self):
        # Arrange
        zone_polygons_data = [{ "vertices": [[0,0], [1,1]] }] # Only 2 vertices
        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)
        # Assert
        self.assertEqual(len(traces), 0)

    def test_single_valid_polygon_default_color(self):
        # Arrange
        vertices = [[0,0], [1,0], [0,1]]
        zone_polygons_data = [{"vertices": vertices}]
        expected_x = [0, 1, 0, 0] # Closed polygon
        expected_y = [0, 0, 1, 0] # Closed polygon
        default_fill_color = "rgba(220,220,220,0.4)"
        default_line_color = "rgba(100, 100, 100, 0.5)"
        default_line_width = 0.5

        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)

        # Assert
        self.assertEqual(len(traces), 1)
        trace = traces[0]
        self.assertIsInstance(trace, go.Scatter)
        self.assertListEqual(list(trace.x), expected_x)
        self.assertListEqual(list(trace.y), expected_y)
        self.assertEqual(trace.mode, "lines")
        self.assertEqual(trace.fill, "toself")
        self.assertEqual(trace.fillcolor, default_fill_color)
        self.assertEqual(trace.line.width, default_line_width)
        self.assertEqual(trace.line.color, default_line_color)
        self.assertEqual(trace.hoverinfo, "skip")
        self.assertEqual(trace.showlegend, False)

    def test_single_valid_polygon_specified_color(self):
        # Arrange
        vertices = [[0,0], [1,1], [0,1]]
        specified_color = "rgba(0,0,255,0.5)" # Blueish
        zone_polygons_data = [{"vertices": vertices, "color": specified_color}]
        expected_x = [0, 1, 0, 0]
        expected_y = [0, 1, 1, 0]

        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)

        # Assert
        self.assertEqual(len(traces), 1)
        trace = traces[0]
        self.assertEqual(trace.fillcolor, specified_color)
        self.assertListEqual(list(trace.x), expected_x)
        self.assertListEqual(list(trace.y), expected_y)

    def test_multiple_polygons_mixed_validity_and_color(self):
        # Arrange
        zone_polygons_data = [
            {"vertices": [[0,0], [1,0], [0,1]]}, # Valid, default color
            {"vertices": [[10,10], [11,10]]},     # Invalid (2 points)
            {"vertices": [[5,5], [6,5], [6,6], [5,6]], "color": "red"}, # Valid, red color
            {"vertices": []} # Invalid (empty vertices)
        ]

        # Act
        traces = create_structural_polygons_traces(zone_polygons_data)

        # Assert
        self.assertEqual(len(traces), 2) # Expecting only 2 valid traces

        # Check first valid trace (default color)
        trace1 = traces[0]
        self.assertEqual(trace1.fillcolor, "rgba(220,220,220,0.4)")
        self.assertListEqual(list(trace1.x), [0,1,0,0])

        # Check second valid trace (red color)
        trace2 = traces[1]
        self.assertEqual(trace2.fillcolor, "red")
        self.assertListEqual(list(trace2.x), [5,6,6,5,5])

class TestPlotUtilsCreateBridgeOutlineTraces(unittest.TestCase):

    def test_empty_lines_data(self):
        # Arrange
        bridge_lines_data = []
        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)
        # Assert
        self.assertEqual(len(traces), 0)
        self.assertIsInstance(traces, list)

    def test_line_missing_start_or_end_key(self):
        # Arrange
        bridge_lines_data = [
            {"end": [1,1]}, # Missing start
            {"start": [0,0]}  # Missing end
        ]
        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)
        # Assert
        self.assertEqual(len(traces), 0)

    def test_line_start_or_end_is_none(self):
        # Arrange
        bridge_lines_data = [
            {"start": None, "end": [1,1]},
            {"start": [0,0], "end": None}
        ]
        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)
        # Assert
        self.assertEqual(len(traces), 0)

    def test_single_valid_line_defaults(self):
        # Arrange
        start_point = [0,0]
        end_point = [10,5]
        bridge_lines_data = [{"start": start_point, "end": end_point}]
        expected_x = [start_point[0], end_point[0]]
        expected_y = [start_point[1], end_point[1]]
        default_color = "grey"
        default_width = 1

        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)

        # Assert
        self.assertEqual(len(traces), 1)
        trace = traces[0]
        self.assertIsInstance(trace, go.Scatter)
        self.assertListEqual(list(trace.x), expected_x)
        self.assertListEqual(list(trace.y), expected_y)
        self.assertEqual(trace.mode, "lines")
        self.assertEqual(trace.line.color, default_color)
        self.assertEqual(trace.line.width, default_width)
        self.assertEqual(trace.hoverinfo, "none")
        self.assertEqual(trace.showlegend, False)

    def test_single_valid_line_specified_color_width(self):
        # Arrange
        start_point = [1,2]
        end_point = [3,4]
        specified_color = "blue"
        specified_width = 3
        bridge_lines_data = [{
            "start": start_point, 
            "end": end_point, 
            "color": specified_color, 
            "width": specified_width
        }]
        expected_x = [start_point[0], end_point[0]]
        expected_y = [start_point[1], end_point[1]]

        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)

        # Assert
        self.assertEqual(len(traces), 1)
        trace = traces[0]
        self.assertListEqual(list(trace.x), expected_x)
        self.assertListEqual(list(trace.y), expected_y)
        self.assertEqual(trace.line.color, specified_color)
        self.assertEqual(trace.line.width, specified_width)

    def test_multiple_lines_mixed_validity(self):
        # Arrange
        bridge_lines_data = [
            {"start": [0,0], "end": [1,1]}, # Valid, default
            {"start": [2,2]},              # Invalid, missing end
            {"start": [3,3], "end": [4,4], "color": "red", "width": 2}, # Valid, specified
            {"start": None, "end": [5,5]}   # Invalid, start is None
        ]

        # Act
        traces = create_bridge_outline_traces(bridge_lines_data)

        # Assert
        self.assertEqual(len(traces), 2) # Expecting 2 valid traces

        # Check first valid trace (default color/width)
        trace1 = traces[0]
        self.assertEqual(trace1.line.color, "grey")
        self.assertEqual(trace1.line.width, 1)
        self.assertListEqual(list(trace1.x), [0,1])

        # Check second valid trace (specified color/width)
        trace2 = traces[1]
        self.assertEqual(trace2.line.color, "red")
        self.assertEqual(trace2.line.width, 2)
        self.assertListEqual(list(trace2.x), [3,4]) 