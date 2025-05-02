"""Module for the Bridge entity parametrization."""

from viktor.parametrization import NumberField, Page, Parametrization, Tab


class BridgeParametrization(Parametrization):
    """Parametrization for the individual Bridge entity."""

    input = Page(
        "Invoer",
        views=["get_3d_view", "get_external_model_view", "get_top_view", "get_longitudinal_section", "get_cross_section"],
    )

    # --- Tabs within Invoer Page ---
    input.geometrie_brug = Tab("Dimensies")
    input.geometrie_wapening = Tab("Wapening")
    input.belastingzones = Tab("Belastingzones")
    input.belastingcombinaties = Tab("Belastingcombinaties")

    # --- Bridge Geometry (moved to geometrie_brug tab) ---
    input.geometrie_brug.lengte = NumberField("Lengte", default=10.0, suffix="m")
    input.geometrie_brug.breedte = NumberField("Breedte", default=5.0, suffix="m")

    # --- Reinforcement Geometry (in geometrie_wapening tab) ---
    input.geometrie_wapening.diameter = NumberField("Diameter", default=12.0, suffix="mm")
    input.geometrie_wapening.spacing = NumberField("h.o.h. Afstand", default=150.0, suffix="mm")
    input.geometrie_wapening.cover = NumberField("Dekking", default=30.0, suffix="mm")

    # --- Load Zones (in belastingzones tab) ---
    input.belastingzones.zone_breedte = NumberField("Zone Breedte", default=1.0, suffix="m")
    input.belastingzones.load_intensity = NumberField("Belasting Intensiteit", default=5.0, suffix="kN/m²")

    # --- Load Combinations (in belastingcombinaties tab) ---
    input.belastingcombinaties.permanent_factor = NumberField("Factor Permanente Belasting", default=1.35)
    input.belastingcombinaties.variable_factor = NumberField("Factor Variabele Belasting", default=1.50)

    # --- Added Pages ---
    scia = Page("SCIA")
    berekening = Page("Berekening")
    rapport = Page("Rapport")
