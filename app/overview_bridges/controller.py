"""Module for the OverviewBridges entity controller."""

from typing import ClassVar

from viktor import ViktorController
from viktor.views import DataItem, DataView, PDFView, PlotlyView

from .parametrization import OverviewBridgesParametrization


class OverviewBridgesController(ViktorController):
    """Controller for the bridge overview entity (parent entity)."""

    label = "Overzicht Bruggen"
    parametrization = OverviewBridgesParametrization
    children: ClassVar[list[str]] = ["Bridge"]  # Defines allowed child entity types
    show_children_as = "Table"  # How children are displayed in the tree

    @DataView("Overzicht", duration_guess=1)
    def get_overview(self, _params: OverviewBridgesParametrization) -> DataView:
        """
        Displays an overview of all bridges in the batch.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A DataView object.
        """
        # Placeholder: Replace with actual overview logic
        data = DataItem("Placeholder", "Overzicht van bruggen komt hier")
        return DataView(data=data)

    @PlotlyView("Vergelijking", duration_guess=1)
    def get_comparison(self, _params: OverviewBridgesParametrization) -> PlotlyView:
        """
        Shows comparison plots of different bridges.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A PlotlyView object.
        """
        # Placeholder: Replace with actual comparison plot logic
        return PlotlyView(data={})  # Replace {} with fig.to_json() when implemented

    @PDFView("Batch Rapport", duration_guess=1)
    def get_batch_report(self, _params: OverviewBridgesParametrization) -> PDFView:
        """
        Generates a batch report potentially containing all bridge reports.

        :param _params: The parametrization instance containing user inputs (unused).
        :return: A PDFView object.
        """
        # Placeholder: Replace with actual batch report generation logic
        return PDFView(html="<h1>Placeholder Batch Rapport</h1>")  # Replace with actual HTML content
