"""Module defining the parametrization for the Bridge entity."""

from viktor.parametrization import (
    BooleanField,
    DateField,
    GeoPointField,
    IntegerField,
    NumberField,
    OptionField,
    Page,
    Tab,
    Text,
    TextField,
    ViktorParametrization,
)


class BridgeParametrization(ViktorParametrization):
    """Defines the input fields and pages for the Bridge entity type."""

    # Bridge Info Page
    bridge_info = Page("Brug info")
    bridge_info.name = TextField("Naam", default="")
    bridge_info.build_year = IntegerField("Bouwjaar", default=2000)
    bridge_info.location = GeoPointField("Locatie op kaart")

    # Input Page with tabs
    input_page = Page("Invoer")

    # Geometry Tab
    input_page.geometry = Tab("Geometrie")
    input_page.geometry.bridge_length = NumberField("Lengte [m]", default=20.0)
    input_page.geometry.bridge_width = NumberField("Breedte [m]", default=10.0)
    input_page.geometry.deck_thickness = NumberField("Dikte brugdek [m]", default=0.5)

    # Loading Zones Tab
    input_page.loading_zones = Tab("Belastingzones")
    input_page.loading_zones.description = Text("Definieer verschillende belastingzones op de brug")
    input_page.loading_zones.num_zones = IntegerField("Aantal zones", default=1, min=1)

    # Load Combinations Tab
    input_page.load_combinations = Tab("Belastingcombinaties")
    input_page.load_combinations.description = Text("Definieer belastingcombinaties volgens Eurocode")
    input_page.load_combinations.include_default_combinations = BooleanField("Standaard combinaties toevoegen", default=True)

    # SCIA Model Settings Tab
    input_page.scia_settings = Tab("SCIA model input")
    input_page.scia_settings.mesh_size = NumberField("Grootte elementen net [m]", default=0.5)
    input_page.scia_settings.download_model = BooleanField("Model te downloaden", default=False)

    # Calculation Page
    calculation = Page("Berekening")
    calculation.run_calculation = BooleanField("Berekening uitvoeren", default=False)
    calculation.calculation_options = OptionField("Rekenopties", options=["Snel", "Normaal", "Uitgebreid"], default="Normaal")

    # Results Page
    results = Page("Resultaten")

    # Cross-section checks
    cross_section = Page("Doorsnede toetsingen")
    cross_section.show_per_combination = BooleanField("Per belastingcombi de resultaten tonen", default=True)
    cross_section.show_max_values = BooleanField("Maatgevende van omhullende combinatie tonen", default=True)

    # Report Page
    report = Page("Rapport")
    report.author = TextField("Opsteller", default="")
    report.date = DateField("Datum", default=None)
    report.include_geometry = BooleanField("Geometrie toevoegen aan rapport", default=True)
    report.include_results = BooleanField("Resultaten toevoegen aan rapport", default=True)
    report.include_checks = BooleanField("Toetsingen toevoegen aan rapport", default=True)
