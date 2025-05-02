"""Module for the Bridge entity controller."""

import plotly.graph_objects as go  # Added Plotly import

from viktor.core import ViktorController
from viktor.geometry import SquareBeam, Vector
from viktor.views import GeometryResult, GeometryView, PlotlyResult, PlotlyView  # Added Plotly imports

# Import parametrization from the separate file
from .parametrization import BridgeParametrization


class BridgeController(ViktorController):
    """Controller for the individual Bridge entity."""

    label = "Brug"
    parametrization = BridgeParametrization  # type: ignore[assignment] # Ignore potential complex assignment MyPy error

    @GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def get_3d_view(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """Generates a simple 3D representation of the bridge deck."""
        length = params.input.geometrie_brug.lengte  # Overall length
        width = params.input.geometrie_brug.breedte  # Width of bridge
        deck_thickness = 0.5  # Thinner deck for realism
        bridge_height = 4.0  # Height from ground to bottom of deck

        # 1. Create the bridge deck at origin, centered in x-y plane
        deck = SquareBeam(width, length, deck_thickness)
        # Center the deck on the origin
        centered_deck = deck.translate(Vector(-width / 2, -length / 2, 0))

        # 2. Move the deck up to the desired height
        elevated_deck = centered_deck.translate(Vector(0, 0, bridge_height))

        return GeometryResult(elevated_deck)

    @PlotlyView("Bovenaanzicht", duration_guess=1)  # Changed to PlotlyView
    def get_top_view(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002 # Changed return type
        """Generates a top view Plotly plot of the bridge deck."""
        fig = go.Figure()
        fig.update_layout(title="Bovenaanzicht (Placeholder)")
        # Add placeholder plot logic here based on params if needed
        return PlotlyResult(fig.to_json())

    @PlotlyView("Langsdoorsnede", duration_guess=1)  # Changed to PlotlyView
    def get_longitudinal_section(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002 # Changed return type
        """Generates a longitudinal section Plotly plot of the bridge deck."""
        fig = go.Figure()
        fig.update_layout(title="Langsdoorsnede (Placeholder)")
        # Add placeholder plot logic here based on params if needed
        return PlotlyResult(fig.to_json())

    @PlotlyView("Dwarsdoorsnede", duration_guess=1)  # Changed to PlotlyView
    def get_cross_section(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002 # Changed return type
        """Generates a cross-section Plotly plot of the bridge deck."""
        fig = go.Figure()
        fig.update_layout(title="Dwarsdoorsnede (Placeholder)")
        # Add placeholder plot logic here based on params if needed
        return PlotlyResult(fig.to_json())
