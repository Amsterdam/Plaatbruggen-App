"""Module for the Bridge entity parametrization."""

from viktor import DynamicArray
from viktor.parametrization import (
    BooleanField,
    DynamicArrayConstraint,
    IsFalse,
    Lookup,
    NumberField,
    Page,
    Parametrization,
    Tab,
    Text,
)


class BridgeParametrization(Parametrization):
    """Parametrization for the individual Bridge entity."""

    input = Page(
        "Invoer",
        views=["get_3d_view", "get_top_view", "get_longitudinal_section", "get_cross_section"],
    )

    # --- Tabs within Invoer Page ---
    input.dimensions = Tab("Dimensies")
    input.geometrie_wapening = Tab("Wapening")
    input.belastingzones = Tab("Belastingzones")
    input.belastingcombinaties = Tab("Belastingcombinaties")

    # --- Bridge Geometry (moved to geometrie_brug tab) ---
    input.dimensions.top_view_loc = NumberField("Locatie bovenaanzicht", default=0.0, suffix="m")
    input.dimensions.longitudinal_section_loc = NumberField("Locatie langsdoorsnede", default=1.0, suffix="m")
    input.dimensions.cross_section_loc = NumberField("Locatie dwarsdoorsnede", default=1.0, suffix="m")

    input.dimensions.segment_explanation = Text(
        """Definieer hier de verschillende segmenten van de brug. Standaard zijn twee segmenten voorgedefinieerd.
Pas de waarden aan of voeg meer segmenten toe via de '+' knop.
Elk segment beschrijft de geometrie tot de volgende snede."""
    )
    input.dimensions.array = DynamicArray(
        "Brug dimensies",
        min=2,
        name="bridge_segments_array",
        default=[
            {
                "bz1": 10.0,
                "bz2": 5.0,
                "bz3": 15.0,
                "dz": 2.0,
                "dze": 1.0,
                "col_6": 0.0,
                "l": 10,
                "is_first_segment": True,
            },
            {
                "bz1": 10.0,
                "bz2": 5.0,
                "bz3": 15.0,
                "dz": 2.0,
                "dze": 1.0,
                "col_6": 0.0,
                "l": 10,
                "is_first_segment": False,
            },
        ],
    )
    input.dimensions.array.is_first_segment = BooleanField("Is First Segment Marker", default=False, visible=False)

    input.dimensions.array.bz1 = NumberField("Breedte zone 1", default=10.0, suffix="m")
    input.dimensions.array.bz2 = NumberField("Breedte zone 2", default=5.0, suffix="m")
    input.dimensions.array.bz3 = NumberField("Breedte zone 3", default=15.0, suffix="m")
    input.dimensions.array.dz = NumberField("Dikte zone 1 en 3", default=2.0, suffix="m")
    input.dimensions.array.dze = NumberField("Extra dikte zone 2", default=1.0, suffix="m")
    input.dimensions.array.col_6 = NumberField("alpha", default=0.0, suffix="Graden")

    _l_field_visibility_constraint = DynamicArrayConstraint(
        dynamic_array_name="bridge_segments_array",
        operand=IsFalse(Lookup("$row.is_first_segment")),
    )
    input.dimensions.array.l = NumberField(
        "Afstand tot vorige snede",
        default=10,
        suffix="m",
        visible=_l_field_visibility_constraint,
    )

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
