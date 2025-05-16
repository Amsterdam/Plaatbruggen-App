"""Module for the Bridge entity parametrization."""

import functools

from viktor import DynamicArray
from viktor.parametrization import (
    BooleanField,
    DynamicArrayConstraint,
    IsFalse,
    Lookup,
    NumberField,
    OptionField,
    Page,
    Parametrization,
    Tab,
    Text,
    TextField,
)

# Define helper functions at the module level


def _get_current_num_segments(params_obj: "BridgeParametrization") -> int:
    """Helper to get the current number of segments from params.bridge_segments_array."""
    try:
        if params_obj is None or not hasattr(params_obj, "bridge_segments_array"):
            return 0

        dimension_array = params_obj.bridge_segments_array

        if dimension_array is None or not isinstance(dimension_array, list | tuple):
            return 0

        return len(dimension_array)
    except Exception:
        return 0


def dx_width_visible_callback(params: "BridgeParametrization", *, x_threshold: int) -> bool:
    """Callback for visibility of dX_width fields."""
    num_segments = _get_current_num_segments(params)
    return num_segments >= x_threshold


# Remove old helper functions if they exist (e.g., _get_dimension_array_length, d3_width_visible, etc.)
# The class definitions below will use the new dX_width_visible_callback

LOAD_ZONE_TYPES = ["Voetgangers", "Fietsers", "Auto"]
MAX_LOAD_ZONE_SEGMENT_FIELDS = 15  # Define how many D-fields (D1 to D15) we'll support for load zones


class BridgeParametrization(Parametrization):
    """Parametrization for the individual Bridge entity."""

    info = Page("Info", views=["get_bridge_map_view"])

    # Hidden fields to store bridge identifiers, moved under the 'info' page
    info.bridge_objectnumm = TextField("Bridge OBJECTNUMM", visible=False)
    info.bridge_name = TextField("Bridge Name", visible=False)

    input = Page(
        "Invoer",
        views=[
            "get_top_view",
            "get_3d_view",
            "get_2d_horizontal_section",
            "get_2d_longitudinal_section",
            "get_2d_cross_section",
            "get_load_zones_view",
        ],
    )

    # --- Tabs within Invoer Page ---
    input.dimensions = Tab("Dimensies")
    input.geometrie_wapening = Tab("Wapening")
    input.belastingzones = Tab("Belastingzones")
    input.belastingcombinaties = Tab("Belastingcombinaties")

    # --- Bridge Geometry (moved to geometrie_brug tab) ---
    input.dimensions.horizontal_section_loc = NumberField("Locatie bovenaanzicht", default=0.0, suffix="m")
    input.dimensions.longitudinal_section_loc = NumberField("Locatie langsdoorsnede", default=1.0, suffix="m")
    input.dimensions.cross_section_loc = NumberField("Locatie dwarsdoorsnede", default=1.0, suffix="m")

    input.dimensions.segment_explanation = Text(
        """Definieer hier de dwarsdoorsneden (snedes) van de brug.
Elk item in de lijst hieronder representeert een dwarsdoorsnede.
- Het **eerste item** definieert de geometrie van het begin van de brug (snede D1).
- Elk **volgend item** definieert de geometrie van de *volgende* dwarsdoorsnede (D2, D3, etc.).
- Het veld '**Afstand tot vorige snede**' (`l`) geeft de lengte van het brugsegment *tussen* de voorgaande en de huidige snede.
  Dit veld is niet zichtbaar voor de eerste snede.
- De overige dimensievelden (zoals `bz1`, `bz2`, `dz` voor de dikte van zone 1 en 3, en `dz_2` voor de dikte van zone 2)
  beschrijven de eigenschappen van de *huidige* dwarsdoorsnede.
Standaard zijn twee dwarsdoorsneden (D1 en D2) voorgedefinieerd, wat resulteert in één brugsegment.
Pas de waarden aan, of voeg meer dwarsdoorsneden toe/verwijder ze via de '+' en '-' knoppen."""
    )
    input.dimensions.array = DynamicArray(
        "Brug dimensies",
        row_label="D-",
        min=2,
        name="bridge_segments_array",
        default=[
            {
                "bz1": 10.0,
                "bz2": 5.0,
                "bz3": 15.0,
                "dz": 2.0,
                "dz_2": 3.0,
                "col_6": 0.0,
                "l": 0,
                "is_first_segment": True,
            },
            {
                "bz1": 10.0,
                "bz2": 5.0,
                "bz3": 15.0,
                "dz": 2.0,
                "dz_2": 3.0,
                "col_6": 0.0,
                "l": 10,
                "is_first_segment": False,
            },
        ],
        # Removed on_update=_update_helper_visibility_fields
    )
    input.dimensions.array.is_first_segment = BooleanField("Is First Segment Marker", default=False, visible=False)

    input.dimensions.array.bz1 = NumberField("Breedte zone 1", default=10.0, suffix="m")
    input.dimensions.array.bz2 = NumberField("Breedte zone 2", default=5.0, suffix="m")
    input.dimensions.array.bz3 = NumberField("Breedte zone 3", default=15.0, suffix="m")
    input.dimensions.array.dz = NumberField("Dikte zone 1 en 3", default=2.0, suffix="m")
    input.dimensions.array.dz_2 = NumberField("Dikte zone 2", default=3.0, suffix="m")
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
    input.belastingzones.info_text = Text(
        "Definieer hier de belastingzones. Elke zone wordt gestapeld vanaf één zijde van de brug. "
        "Vul alleen breedtes in voor de daadwerkelijk gedefinieerde brugsegmenten (D-nummers) "
        "onder de tab 'Dimensies'."
    )

    input.belastingzones.load_zones_array = DynamicArray(
        "Belastingzones",
        row_label="Zone",
        default=[
            {
                "zone_type": LOAD_ZONE_TYPES[0],
                "d1_width": 1.0,
                "d2_width": 1.0,
                "d3_width": 0.0,
                "d4_width": 0.0,
                "d5_width": 0.0,
                "d6_width": 0.0,
                "d7_width": 0.0,
                "d8_width": 0.0,
                "d9_width": 0.0,
                "d10_width": 0.0,
                "d11_width": 0.0,
                "d12_width": 0.0,
                "d13_width": 0.0,
                "d14_width": 0.0,
                "d15_width": 0.0,
            },
            {
                "zone_type": LOAD_ZONE_TYPES[1] if len(LOAD_ZONE_TYPES) > 1 else LOAD_ZONE_TYPES[0],
                "d1_width": 1.0,
                "d2_width": 1.0,
                "d3_width": 0.0,
                "d4_width": 0.0,
                "d5_width": 0.0,
                "d6_width": 0.0,
                "d7_width": 0.0,
                "d8_width": 0.0,
                "d9_width": 0.0,
                "d10_width": 0.0,
                "d11_width": 0.0,
                "d12_width": 0.0,
                "d13_width": 0.0,
                "d14_width": 0.0,
                "d15_width": 0.0,
            },
        ],
    )
    input.belastingzones.load_zones_array.zone_type = OptionField("Type belastingzone", options=LOAD_ZONE_TYPES, default=LOAD_ZONE_TYPES[0])
    input.belastingzones.load_zones_array.d1_width = NumberField(
        "Breedte zone bij D1", default=1.0, suffix="m", description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D1."
    )
    input.belastingzones.load_zones_array.d2_width = NumberField(
        "Breedte zone bij D2", default=1.0, suffix="m", description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D2."
    )

    input.belastingzones.load_zones_array.d3_width = NumberField(
        "Breedte zone bij D3",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=3),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D3.",
    )
    input.belastingzones.load_zones_array.d4_width = NumberField(
        "Breedte zone bij D4",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=4),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D4.",
    )
    input.belastingzones.load_zones_array.d5_width = NumberField(
        "Breedte zone bij D5",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=5),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D5.",
    )
    input.belastingzones.load_zones_array.d6_width = NumberField(
        "Breedte zone bij D6",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=6),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D6.",
    )
    input.belastingzones.load_zones_array.d7_width = NumberField(
        "Breedte zone bij D7",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=7),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D7.",
    )
    input.belastingzones.load_zones_array.d8_width = NumberField(
        "Breedte zone bij D8",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=8),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D8.",
    )
    input.belastingzones.load_zones_array.d9_width = NumberField(
        "Breedte zone bij D9",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=9),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D9.",
    )
    input.belastingzones.load_zones_array.d10_width = NumberField(
        "Breedte zone bij D10",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=10),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D10.",
    )
    input.belastingzones.load_zones_array.d11_width = NumberField(
        "Breedte zone bij D11",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=11),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D11.",
    )
    input.belastingzones.load_zones_array.d12_width = NumberField(
        "Breedte zone bij D12",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=12),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D12.",
    )
    input.belastingzones.load_zones_array.d13_width = NumberField(
        "Breedte zone bij D13",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=13),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D13.",
    )
    input.belastingzones.load_zones_array.d14_width = NumberField(
        "Breedte zone bij D14",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=14),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D14.",
    )
    input.belastingzones.load_zones_array.d15_width = NumberField(
        "Breedte zone bij D15",
        default=0.0,
        suffix="m",
        visible=functools.partial(dx_width_visible_callback, x_threshold=15),
        description="Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D15.",
    )

    # --- Load Combinations (in belastingcombinaties tab) ---
    input.belastingcombinaties.permanent_factor = NumberField("Factor Permanente Belasting", default=1.35)
    input.belastingcombinaties.variable_factor = NumberField("Factor Variabele Belasting", default=1.50)

    # --- Added Pages ---
    scia = Page("SCIA")
    berekening = Page("Berekening")
    rapport = Page("Rapport", views=["get_output_report"])
