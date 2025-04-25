"""Module defining the parametrization for the OverviewBridges entity."""

from viktor.parametrization import BooleanField, ChildEntityManager, NumberField, Page, Text, TextField, ViktorParametrization


class OverviewBridgesParametrization(ViktorParametrization):
    """Defines the input fields and pages for the OverviewBridges entity type."""

    # Batch Info
    info = Page("Overzicht Informatie")
    info.title = TextField("Titel", default="Overzicht Bruggen")
    info.description = TextField("Beschrijving", default="")
    info.intro = Text("# Automatisch Toetsmodel Plaatbruggen\nVoeg hier bruggen toe aan het overzicht.")

    # Bridges Management
    info.bridges = ChildEntityManager("Bridge")

    # Batch Calculation Settings
    calculation = Page("Batch berekening")
    calculation.run_all = BooleanField("Alle bruggen berekenen", default=False)
    calculation.parallel = BooleanField("Parallel berekenen", default=True)
    calculation.max_parallel = NumberField("Maximum aantal parallelle berekeningen", default=4, min=1, max=8)

    # Batch Results
    results = Page("Batch resultaten")
    results.description = Text("Hier worden de resultaten van alle bruggen weergegeven.")

    # Batch Report
    report = Page("Batch rapport")
    report.generate = BooleanField("Rapport genereren", default=False)
    report.include_all_bridges = BooleanField("Alle bruggen opnemen", default=True)
    report.author = TextField("Opsteller", default="")
