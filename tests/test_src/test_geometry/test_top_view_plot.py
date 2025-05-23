import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import plotly.graph_objects as go
from munch import Munch # type: ignore[import-untyped]
from typing import Any

from src.geometry.top_view_plot import build_top_view_figure

class TestTopViewPlot(unittest.TestCase):

    def _create_default_geometric_data(self) -> dict[str, Any]:
        """Helper to create a basic geometric data dictionary."""
        return {
            "zone_polygons": [],
            "bridge_lines": [],
            "zone_annotations": [],
            "dimension_texts": [],
            "cross_section_labels": [],
        }

    def test_build_top_view_figure_empty_data_no_warnings(self):
        """Test with empty geometric data and no validation warnings."""
        geo_data = self._create_default_geometric_data()
        fig = build_top_view_figure(geo_data)

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0) # No traces expected
        self.assertEqual(len(fig.layout.annotations), 0) # No annotations expected

        # Check basic layout properties
        self.assertEqual(fig.layout.title.text, "Bovenaanzicht (Top View)")
        self.assertEqual(fig.layout.xaxis.title.text, "Length (m)")
        self.assertEqual(fig.layout.yaxis.title.text, "Width (m)")
        self.assertFalse(fig.layout.showlegend)
        self.assertTrue(fig.layout.autosize)
        self.assertEqual(fig.layout.hovermode, "closest")
        self.assertEqual(fig.layout.yaxis.scaleanchor, "x")
        self.assertEqual(fig.layout.yaxis.scaleratio, 1)
        self.assertEqual(fig.layout.margin.l, 0)
        self.assertEqual(fig.layout.margin.r, 50)
        self.assertEqual(fig.layout.margin.t, 50)
        self.assertEqual(fig.layout.margin.b, 115)
        self.assertEqual(fig.layout.plot_bgcolor, "white")

    def test_build_top_view_figure_with_validation_warnings(self):
        """Test with validation warnings."""
        geo_data = self._create_default_geometric_data()
        warnings = ["Warning 1", "Another warning here."]
        fig = build_top_view_figure(geo_data, validation_messages=warnings)

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0)
        self.assertEqual(len(fig.layout.annotations), 1) # One consolidated warning annotation

        warning_annotation = fig.layout.annotations[0]
        self.assertIn("<b>Waarschuwing (Belastingzones):</b> Warning 1", warning_annotation.text)
        self.assertIn("<b>Waarschuwing (Belastingzones):</b> Another warning here.", warning_annotation.text)
        self.assertEqual(warning_annotation.font.color, "orangered")
        self.assertEqual(warning_annotation.font.size, 13)

    def test_build_top_view_figure_with_zone_polygons(self):
        """Test figure creation with zone polygon data."""
        geo_data = self._create_default_geometric_data()
        geo_data["zone_polygons"] = [
            {
                "vertices": [[0, 0], [1, 0], [1, 1], [0, 1]],
                "color": "rgba(255,0,0,0.5)"
            },
            {
                "vertices": [[2, 2], [3, 2], [3, 3], [2, 3]], # Polygon without color
            },
            {"vertices": []} # Empty vertices, should be skipped
        ]
        fig = build_top_view_figure(geo_data)

        self.assertEqual(len(fig.data), 2) # Two valid polygons
        polygon_trace_1 = fig.data[0]
        self.assertEqual(list(polygon_trace_1.x), [0, 1, 1, 0, 0])
        self.assertEqual(list(polygon_trace_1.y), [0, 0, 1, 1, 0])
        self.assertEqual(polygon_trace_1.fill, "toself")
        self.assertEqual(polygon_trace_1.fillcolor, "rgba(255,0,0,0.5)")
        self.assertEqual(polygon_trace_1.line.width, 0)
        self.assertEqual(polygon_trace_1.hoverinfo, "skip")
        self.assertFalse(polygon_trace_1.showlegend)

        polygon_trace_2 = fig.data[1]
        self.assertEqual(list(polygon_trace_2.x), [2, 3, 3, 2, 2])
        self.assertEqual(list(polygon_trace_2.y), [2, 2, 3, 3, 2])
        self.assertEqual(polygon_trace_2.fillcolor, "rgba(128,128,128,0.1)") # Default color

    def test_build_top_view_figure_with_bridge_lines(self):
        """Test figure creation with bridge line data."""
        geo_data = self._create_default_geometric_data()
        geo_data["bridge_lines"] = [
            {"start": [0, 0], "end": [10, 0], "name_hint": "Segment 0"}, # Added name_hint for clarity in test
            {"start": [0, 5], "end": [10, 5], "name_hint": "Segment 1"},
        ]
        fig = build_top_view_figure(geo_data)

        self.assertIsInstance(fig, go.Figure)
        # We expect 2 traces from bridge_lines based on the input
        self.assertEqual(len(fig.data), 2, "Incorrect number of data traces found for bridge lines.")

        # --- Check Trace 0 --- 
        trace_0_name = "Bridge Outline Segment 0"
        bridge_line_trace_0 = None
        for trace in fig.data:
            if hasattr(trace, "name") and trace.name == trace_0_name:
                bridge_line_trace_0 = trace
                break
        
        self.assertIsNotNone(bridge_line_trace_0, f"Trace '{trace_0_name}' not found.")
        assert bridge_line_trace_0 is not None # for mypy

        self.assertEqual(bridge_line_trace_0.mode, "lines")
        expected_x_0 = [geo_data["bridge_lines"][0]["start"][0], geo_data["bridge_lines"][0]["end"][0]]
        expected_y_0 = [geo_data["bridge_lines"][0]["start"][1], geo_data["bridge_lines"][0]["end"][1]]
        self.assertEqual(list(bridge_line_trace_0.x), expected_x_0)
        self.assertEqual(list(bridge_line_trace_0.y), expected_y_0)
        self.assertEqual(bridge_line_trace_0.line.color, "blue") # SUT uses blue
        self.assertEqual(bridge_line_trace_0.line.width, 2)
        self.assertEqual(bridge_line_trace_0.hoverinfo, "none")
        self.assertFalse(bridge_line_trace_0.showlegend)

        # --- Check Trace 1 --- 
        trace_1_name = "Bridge Outline Segment 1"
        bridge_line_trace_1 = None
        for trace in fig.data:
            if hasattr(trace, "name") and trace.name == trace_1_name:
                bridge_line_trace_1 = trace
                break
        
        self.assertIsNotNone(bridge_line_trace_1, f"Trace '{trace_1_name}' not found.")
        assert bridge_line_trace_1 is not None # for mypy

        self.assertEqual(bridge_line_trace_1.mode, "lines")
        expected_x_1 = [geo_data["bridge_lines"][1]["start"][0], geo_data["bridge_lines"][1]["end"][0]]
        expected_y_1 = [geo_data["bridge_lines"][1]["start"][1], geo_data["bridge_lines"][1]["end"][1]]
        self.assertEqual(list(bridge_line_trace_1.x), expected_x_1)
        self.assertEqual(list(bridge_line_trace_1.y), expected_y_1)
        self.assertEqual(bridge_line_trace_1.line.color, "blue")
        self.assertEqual(bridge_line_trace_1.line.width, 2)
        self.assertEqual(bridge_line_trace_1.hoverinfo, "none")
        self.assertFalse(bridge_line_trace_1.showlegend)

    def test_build_top_view_figure_with_zone_annotations(self):
        """Test figure creation with zone annotation data."""
        geo_data = self._create_default_geometric_data()
        geo_data["zone_annotations"] = [
            {"x": 1, "y": 2, "text": "Zone A"},
            {"x": 5, "y": 6, "text": "Zone B"},
        ]
        fig = build_top_view_figure(geo_data)

        self.assertEqual(len(fig.layout.annotations), 2)
        ann_1 = fig.layout.annotations[0]
        self.assertEqual(ann_1.x, 1)
        self.assertEqual(ann_1.y, 2)
        self.assertEqual(ann_1.text, "<b>Zone A</b>")
        self.assertFalse(ann_1.showarrow)
        self.assertEqual(ann_1.font.size, 14)
        self.assertEqual(ann_1.font.color, "DarkSlateGray")

    def test_build_top_view_figure_with_dimension_texts(self):
        """Test figure creation with dimension text data, covering different alignments."""
        geo_data = self._create_default_geometric_data()
        geo_data["dimension_texts"] = [
            {"x": 1, "y": 1, "text": "Default", "type": "width"}, # Default (left, middle)
            {"x": 2, "y": 2, "text": "Length", "type": "length"}, # (center, bottom)
            {"x": 3, "y": 3, "text": "Rotated 180", "textangle": 180}, # (right, middle)
            {"x": 4, "y": 4, "text": "Rotated 90", "textangle": 90}, # (center, middle)
            {"x": 5, "y": 5, "text": "Rotated -90", "textangle": -90}, # (center, middle)
            {"x": 6, "y": 6, "text": "Explicit Center", "align": "center", "xanchor": "center", "yanchor": "middle"} # Explicit values
        ]
        fig = build_top_view_figure(geo_data)
        self.assertEqual(len(fig.layout.annotations), 6)

        # Default (type: width)
        ann_default = next(a for a in fig.layout.annotations if a.text == "<b>Default</b>")
        self.assertEqual(ann_default.align, "left")
        self.assertEqual(ann_default.xanchor, "left")
        self.assertEqual(ann_default.yanchor, "middle")

        # Type: length
        ann_length = next(a for a in fig.layout.annotations if a.text == "<b>Length</b>")
        self.assertEqual(ann_length.align, "center")
        self.assertEqual(ann_length.xanchor, "center")
        self.assertEqual(ann_length.yanchor, "bottom")

        # Rotated 180
        ann_rot180 = next(a for a in fig.layout.annotations if a.text == "<b>Rotated 180</b>")
        self.assertEqual(ann_rot180.align, "right")
        self.assertEqual(ann_rot180.xanchor, "right")
        self.assertEqual(ann_rot180.yanchor, "middle")
        self.assertTrue(ann_rot180.textangle == 180 or ann_rot180.textangle == -180)

        # Rotated 90
        ann_rot90 = next(a for a in fig.layout.annotations if a.text == "<b>Rotated 90</b>")
        self.assertEqual(ann_rot90.align, "center")
        self.assertEqual(ann_rot90.xanchor, "center")
        self.assertEqual(ann_rot90.yanchor, "middle")
        self.assertEqual(ann_rot90.textangle, 90)

    @patch("src.geometry.top_view_plot.create_text_annotations_from_data")
    def test_build_top_view_figure_with_cross_section_labels(self, mock_create_text_annotations):
        """Test figure creation with cross section label data."""
        geo_data = self._create_default_geometric_data()
        cs_label_data = [{"x": 1, "y": 1, "text": "CS1"}]
        geo_data["cross_section_labels"] = cs_label_data
        
        mock_cs_annotations = [go.layout.Annotation(text="Mocked CS Anno")]
        mock_create_text_annotations.return_value = mock_cs_annotations

        fig = build_top_view_figure(geo_data)

        mock_create_text_annotations.assert_called_once_with(
            label_data=cs_label_data,
            font_size=15,
            font_color="black",
            align="center",
            xanchor="center",
            yanchor="bottom",
        )
        self.assertIn(mock_cs_annotations[0], fig.layout.annotations)
        self.assertEqual(len(fig.layout.annotations), 1)

    @patch("src.geometry.top_view_plot.create_text_annotations_from_data")
    def test_build_top_view_figure_with_all_data_types(self, mock_create_text_annotations):
        """Test with all data types present and a validation warning."""
        geo_data = {
            "zone_polygons": [{"vertices": [[0,0],[1,0],[0,1]], "color":"red"}],
            "bridge_lines": [{"start":[0,0], "end":[1,0]}],
            "zone_annotations": [{"x":0.5, "y":0.5, "text":"Z1"}],
            "dimension_texts": [{"x":1, "y":1, "text":"Dim1", "type":"length"}],
            "cross_section_labels": [{"x":2, "y":2, "text":"CS-A"}]
        }
        warnings = ["Test Warning"]
        
        mock_cs_anno_instance = go.layout.Annotation(text="Mocked CS Anno for All Data")
        mock_create_text_annotations.return_value = [mock_cs_anno_instance]

        fig = build_top_view_figure(geo_data, validation_messages=warnings)

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 2) # 1 polygon + 1 line
        self.assertEqual(len(fig.layout.annotations), 4) # zone, dim, cs, warning

        # Check polygon trace
        self.assertEqual(list(fig.data[0].x), [0,1,0,0])
        self.assertEqual(fig.data[0].fillcolor, "red")

        # Check line trace
        self.assertEqual(list(fig.data[1].x), [0,1])

        # Check presence of annotations (order might vary, so check by content or type)
        texts = [ann.text for ann in fig.layout.annotations]
        self.assertIn("<b>Z1</b>", texts)
        self.assertIn("<b>Dim1</b>", texts)
        self.assertIn("Mocked CS Anno for All Data", texts)
        self.assertIn("<b>Waarschuwing (Belastingzones):</b> Test Warning", texts)

        mock_create_text_annotations.assert_called_once_with(
            label_data=geo_data["cross_section_labels"],
            font_size=15, # Match args in build_top_view_figure
            font_color="black",
            align="center",
            xanchor="center",
            yanchor="bottom",
        )

    # Add more tests for zone polygons, bridge lines, zone annotations, dimension texts, cross section labels

if __name__ == "__main__":
    unittest.main() 