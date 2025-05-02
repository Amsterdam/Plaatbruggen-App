"""Module for the Bridge entity controller."""

from viktor.core import ViktorController
from viktor.geometry import SquareBeam, Vector
from viktor.views import GeometryResult, GeometryView

# Import parametrization from the separate file
from .parametrization import BridgeParametrization


class BridgeController(ViktorController):
    """Controller for the individual Bridge entity."""

    label = "Brug"
    parametrization = BridgeParametrization  # type: ignore[assignment] # Ignore potential complex assignment MyPy error

    @GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def get_3d_view(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """Generates a simple 3D representation of the bridge deck."""
        length = params.lengte  # Overall length
        width = params.breedte  # Width of bridge
        deck_thickness = 0.5  # Thinner deck for realism
        bridge_height = 4.0  # Height from ground to bottom of deck

        # 1. Create the bridge deck at origin, centered in x-y plane
        deck = SquareBeam(width, length, deck_thickness)
        # Center the deck on the origin
        centered_deck = deck.translate(Vector(-width / 2, -length / 2, 0))

        # 2. Move the deck up to the desired height
        elevated_deck = centered_deck.translate(Vector(0, 0, bridge_height))

        return GeometryResult(elevated_deck)
