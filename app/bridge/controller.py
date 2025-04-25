"""Module for the Bridge entity controller."""

from viktor import UserError, ViktorController
from viktor.views import DataItem, DataView, GeometryView, MapPoint, MapView, PDFView, PlotlyView

from .parametrization import BridgeParametrization


class BridgeController(ViktorController):
    """Controller for individual bridge entities (child entities)."""

    label = "Brug"
    parametrization = BridgeParametrization

    @MapView("Kaart", duration_guess=1)
    def get_map_view(self, params: BridgeParametrization) -> MapView:
        """
        Displays the bridge location on a map.

        :param params: The parametrization instance containing user inputs.
        :return: A MapView object.
        :raises UserError: If the location is not set.
        """
        features: list[MapPoint] = []
        if params.bridge_info.location:
            features.append(MapPoint.from_geo_point(params.bridge_info.location))
        else:
            raise UserError("Locatie niet ingesteld in de 'Brug info' pagina.")
        return MapView(features=features)

    @DataView("Resultaten Overzicht", duration_guess=1)
    def get_results_overview(self, _params: BridgeParametrization) -> DataView:
        """
        Shows calculation results in a table.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A DataView object.
        """
        # Placeholder: Replace with actual result fetching and formatting
        data = DataItem("Placeholder", "Resultaten komen hier")
        return DataView(data=data)

    @GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def get_geometry_view(self, _params: BridgeParametrization) -> GeometryView:
        """
        Generates a 3D visualization of the bridge.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A GeometryView object.
        """
        # Placeholder: Replace with actual geometry generation logic
        return GeometryView()  # Add geometry_result=example_geometry when implemented

    @PlotlyView("Grafieken", duration_guess=1)
    def get_plots(self, _params: BridgeParametrization) -> PlotlyView:
        """
        Creates plots of analysis results.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A PlotlyView object.
        """
        # Placeholder: Replace with actual plot generation logic
        return PlotlyView(data={})  # Replace {} with fig.to_json() when implemented

    @PDFView("Rapport", duration_guess=1)
    def get_report(self, _params: BridgeParametrization) -> PDFView:
        """
        Generates a PDF report.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A PDFView object.
        """
        # Placeholder: Replace with actual report generation logic
        return PDFView(html="<h1>Placeholder Rapport</h1>")  # Replace with actual HTML content
