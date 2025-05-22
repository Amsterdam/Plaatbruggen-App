"""Module for the Bridge entity parametrization."""

from collections.abc import Callable, Mapping
from typing import Any

from app.constants import LOAD_ZONE_TYPES, MAX_LOAD_ZONE_SEGMENT_FIELDS
from viktor import DynamicArray
from viktor.parametrization import (
    BooleanField,
    DynamicArrayConstraint,
    IsFalse,
    LineBreak,
    Lookup,
    NumberField,
    OptionField,
    Page,
    Parametrization,
    Tab,
    Text,
    TextField,
)

from .geometry_functions import get_steel_qualities

# --- Helper functions for DynamicArray Default Rows ---


def _create_default_dimension_segment_row(l_value: int, is_first: bool) -> dict[str, Any]:
    """Creates a dictionary for a default bridge dimension segment row."""
    return {
        "bz1": 10.0,
        "bz2": 5.0,
        "bz3": 15.0,
        "dz": 2.0,
        "dz_2": 3.0,
        "col_6": 0.0,
        "l": l_value,
        "is_first_segment": is_first,
    }


def _create_default_load_zone_row(zone_type: str, default_width: float) -> dict[str, Any]:
    """Creates a dictionary for a default load zone row."""
    row: dict[str, Any] = {"zone_type": zone_type}
    for i in range(1, MAX_LOAD_ZONE_SEGMENT_FIELDS + 1):
        row[f"d{i}_width"] = default_width
    return row


# --- Helper functions for Parametrization Logic (e.g., visibility callbacks) ---
def _get_current_num_load_zones(params_obj: "BridgeParametrization") -> int:
    """Helper to get the current number of load zones from params.load_zones_data_array."""
    try:
        if params_obj is None or not hasattr(params_obj, "load_zones_data_array"):
            return 0
        load_zones_array = params_obj.load_zones_data_array
        if load_zones_array is None or not isinstance(load_zones_array, list | tuple):
            return 0
        return len(load_zones_array)
    except (AttributeError, TypeError):
        # Parameters not yet fully defined during app initialization or update – treat as "0" zones
        return 0


def _get_current_num_segments(params_obj: "BridgeParametrization") -> int:
    """Helper to get the current number of segments from params.bridge_segments_array."""
    try:
        if params_obj is None or not hasattr(params_obj, "bridge_segments_array"):
            return 0
        dimension_array = params_obj.bridge_segments_array
        if dimension_array is None or not isinstance(dimension_array, list | tuple):
            return 0
        return len(dimension_array)
    except (AttributeError, TypeError):
        # Parameters not yet fully defined during app initialization or update – treat as "0" segments
        return 0


# Factory function to create visibility callbacks for dX_width fields
def _create_dx_width_visibility_callback(required_segment_count: int) -> Callable[..., list[bool]]:
    """
    Factory function to create visibility callback functions for dX_width fields.

    Args:
        required_segment_count: The minimum number of bridge segments (D-sections)
                                that must exist for the dX_width field to be
                                potentially visible (before considering the last row rule).

    Returns:
        A callback function suitable for the 'visible' attribute of a NumberField.

    """

    def dx_width_visibility_function(params, **kwargs) -> list[bool]:  # noqa: ANN001, ARG001
        """
        Determines visibility for a dX_width field in the load_zones_array.

        A row's field is visible if:
        1. The number of defined bridge segments is >= required_segment_count.
        2. The row is not the last row in the load_zones_array.
        """
        num_segments = _get_current_num_segments(params)
        num_load_zones = _get_current_num_load_zones(params)

        if num_load_zones <= 0:
            return []

        visibility_list = []
        for i in range(num_load_zones):
            is_visible = (num_segments >= required_segment_count) and (i < num_load_zones - 1)
            visibility_list.append(is_visible)

        return visibility_list

    return dx_width_visibility_function


# Generate the visibility callbacks using a dictionary comprehension
DX_WIDTH_VISIBILITY_CALLBACKS = {i: _create_dx_width_visibility_callback(i) for i in range(1, MAX_LOAD_ZONE_SEGMENT_FIELDS + 1)}


# --- Functions for dynamic reinforcement zones ---
def calculate_max_array(params: Mapping, **kwargs) -> int:  # noqa: ARG001
    """
    Calculate the maximum number of reinforcement zones based on bridge segments.

    Args:
        params: Parameters object containing bridge_segments_array
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The maximum number of reinforcement zones (3 per segment)

    """
    sections = len(params.bridge_segments_array)
    return 3 * (sections - 1)


def define_options_numbering(params: Mapping, **kwargs) -> list:  # noqa: ARG001
    """
    Define options for zone numbering based on the number of segments.

    Args:
        params: Parameters containing bridge_segments_array
        **kwargs: Additional keyword arguments (unused).

    Returns:
        list: List of zone numbers in format "location-segment" (e.g., ["1-1", "2-1", "3-1", "1-2", "2-2", "3-2"])

    """
    option_list = []
    num_segments = len(params.bridge_segments_array) - 1
    # For each segment
    for segment in range(num_segments):
        # For each zone (left, middle, right)
        for zone in range(3):
            zone_number = f"{zone + 1}-{segment + 1}"
            option_list.append(zone_number)
    return option_list


class BridgeParametrization(Parametrization):
    """Parametrization for the individual Bridge entity."""

    ###############################################
    ## Info Page
    ##############################################

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

    ###############################################
    ## Invoer Page
    ##############################################

    # --- Tabs within Invoer Page ---
    input.dimensions = Tab("Dimensies")
    input.geometrie_wapening = Tab("Wapening")
    input.belastingzones = Tab("Belastingzones")
    input.belastingcombinaties = Tab("Belastingcombinaties")

    # ----------------------------------------
    ## Dimensions tab
    # ----------------------------------------

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
            _create_default_dimension_segment_row(l_value=0, is_first=True),
            _create_default_dimension_segment_row(l_value=10, is_first=False),
        ],
    )
    input.dimensions.array.is_first_segment = BooleanField("Is First Segment Marker", default=False, visible=False)

    input.dimensions.array.bz1 = NumberField("Breedte zone 1", default=10.0, suffix="m")
    input.dimensions.array.bz2 = NumberField("Breedte zone 2", default=5.0, suffix="m")
    input.dimensions.array.bz3 = NumberField("Breedte zone 3", default=15.0, suffix="m")
    input.dimensions.array.dz = NumberField("Dikte zone 1 en 3", default=2.0, suffix="m")
    input.dimensions.array.dz_2 = NumberField("Dikte zone 2", default=3.0, suffix="m")
    input.dimensions.array.col_6 = NumberField("alpha", default=0.0, suffix="Graden", visible=False)

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

    # --- Bridge Geometry (moved to geometrie_brug tab) ---
    input.dimensions.lb1 = LineBreak()
    input.dimensions.text_sections = Text("Met onderstaande instellingen kan de locatie van de doorsneden worden ingesteld.")
    input.dimensions.toggle_sections = BooleanField("Toon locaties van de doorsneden in het 3D model", default=False, flex=100)
    input.dimensions.lb2 = LineBreak()
    input.dimensions.horizontal_section_loc = NumberField(
        "Horizontale doorsnede z =", default=-1.0, suffix="m", visible=Lookup("input.dimensions.toggle_sections")
    )
    input.dimensions.lb3 = LineBreak()
    input.dimensions.longitudinal_section_loc = NumberField(
        "Langsdoorsnede y =", default=0.0, suffix="m", visible=Lookup("input.dimensions.toggle_sections")
    )
    input.dimensions.lb4 = LineBreak()
    input.dimensions.cross_section_loc = NumberField(
        "Dwarsdoorsnede x =", default=0.0, suffix="m", visible=Lookup("input.dimensions.toggle_sections")
    )

    # --- Reinforcement Geometry (in geometrie_wapening tab) ---
    input.geometrie_wapening.explanation = Text(
        """Op deze pagina kan de wapening van de brug worden ingevoerd. De wapening moet ingevoerd worden per zone.
De zones corresponderen met de plaatzones die worden gegenereerd op basis van de geometrie:
- Bij de minimale geometrie (2 doorsnedes) ontstaan er 3 zones: "1-1", "2-1" en "3-1"
- Voor elke extra doorsnede komen er 3 nieuwe zones bij: "1-2", "2-2", "3-2", etc.
- Het getal voor het streepje correspondeert met de zone (1=links, 2=midden, 3=rechts)
- Het getal na het streepje geeft aan bij welk segment de zone hoort

Eerst wordt er gevraagd naar de eigenschappen van de hoofdwapening in langs- en dwarsrichting.
Vervolgens kan er per veld aangeklikt worden, of er extra bijlegwapening aanwezig is in de zone.
Wanneer dit wordt aangevinkt, verschijnen dezelfde invoervelden nogmaals, om deze bijlegwapening te definiëren.
In het model, wordt deze bijlegwapening automatisch tussen het bestaande hoofdwapeningsnet gelegd."""
    )  # General reinforcement parameters
    input.geometrie_wapening.staalsoort = OptionField(
        "Staalsoort",
        options=get_steel_qualities(),
        default="B500B",  # Changed to more modern default
        description="De kwaliteit van het betonstaal dat wordt toegepast in de brug.",
    )

    input.geometrie_wapening.dekking = NumberField(
        "Betondekking",
        default=55.0,
        suffix="mm",
        description="De betondekking is de afstand tussen de buitenkant van het beton en de buitenste wapeningslaag.",
    )
    input.geometrie_wapening.langswapening_buiten = BooleanField(
        "Langswapening aan buitenzijde?",
        default=True,
        description=(
            "Indien aangevinkt ligt de langswapening aan de buitenzijde van het beton. Indien uitgevinkt ligt de dwarswapening aan de buitenzijde."
        ),
    )

    input.geometrie_wapening.zones = DynamicArray(
        "Wapening per zone",
        min=3,
        max=calculate_max_array,
        name="reinforcement_zones_array",
        default=[
            {
                "zone_number": "1-1",
                "hoofdwapening_langs_boven_diameter": 12.0,
                "hoofdwapening_langs_boven_hart_op_hart": 150.0,
                "hoofdwapening_langs_onder_diameter": 12.0,
                "hoofdwapening_langs_onder_hart_op_hart": 150.0,
                "hoofdwapening_dwars_diameter": 12.0,
                "hoofdwapening_dwars_hart_op_hart": 150.0,
                "heeft_bijlegwapening": False,
            },
            {
                "zone_number": "2-1",
                "hoofdwapening_langs_boven_diameter": 12.0,
                "hoofdwapening_langs_boven_hart_op_hart": 150.0,
                "hoofdwapening_langs_onder_diameter": 12.0,
                "hoofdwapening_langs_onder_hart_op_hart": 150.0,
                "hoofdwapening_dwars_diameter": 12.0,
                "hoofdwapening_dwars_hart_op_hart": 150.0,
                "heeft_bijlegwapening": False,
            },
            {
                "zone_number": "3-1",
                "hoofdwapening_langs_boven_diameter": 12.0,
                "hoofdwapening_langs_boven_hart_op_hart": 150.0,
                "hoofdwapening_langs_onder_diameter": 12.0,
                "hoofdwapening_langs_onder_hart_op_hart": 150.0,
                "hoofdwapening_dwars_diameter": 12.0,
                "hoofdwapening_dwars_hart_op_hart": 150.0,
                "heeft_bijlegwapening": False,
            },
        ],
    )

    # Zone number display
    input.geometrie_wapening.zones.zone_number = OptionField(
        "Zone nummer", options=define_options_numbering, description="Dit is het zone nummer dat correspondeert met de zone in de brug."
    )

    input.geometrie_wapening.zones.lb1 = LineBreak()

    # Main reinforcement - Longitudinal top
    input.geometrie_wapening.zones.hoofdwapening_langs_boven_diameter = NumberField(
        "Diameter hoofdwapening langsrichting boven", default=12.0, suffix="mm", flex=47
    )
    input.geometrie_wapening.zones.hoofdwapening_langs_boven_hart_op_hart = NumberField(
        "H.o.h. afstand hoofdwapening langsrichting boven", default=150.0, suffix="mm", flex=53
    )
    input.geometrie_wapening.zones.lb2 = LineBreak()

    # Main reinforcement - Longitudinal bottom
    input.geometrie_wapening.zones.hoofdwapening_langs_onder_diameter = NumberField(
        "Diameter hoofdwapening langsrichting onder", default=12.0, suffix="mm", flex=47
    )
    input.geometrie_wapening.zones.hoofdwapening_langs_onder_hart_op_hart = NumberField(
        "H.o.h. afstand hoofdwapening langsrichting onder", default=150.0, suffix="mm", flex=53
    )
    input.geometrie_wapening.zones.lb3 = LineBreak()

    # Main reinforcement - Transverse

    input.geometrie_wapening.zones.hoofdwapening_dwars_diameter = NumberField(
        "Diameter hoofdwapening dwarsrichting", default=12.0, suffix="mm", flex=47
    )

    input.geometrie_wapening.zones.hoofdwapening_dwars_hart_op_hart = NumberField(
        "H.o.h. afstand hoofdwapening dwarsrichting", default=150.0, suffix="mm", flex=53
    )

    # Visual separator for bijlegwapening
    input.geometrie_wapening.zones.separator1 = LineBreak()

    # Additional reinforcement toggle
    input.geometrie_wapening.zones.heeft_bijlegwapening = BooleanField("Bijlegwapening aanwezig?", default=False)

    # Additional reinforcement fields - only visible when heeft_bijlegwapening is True
    _bijleg_visibility = DynamicArrayConstraint(
        dynamic_array_name="reinforcement_zones_array",
        operand=Lookup("$row.heeft_bijlegwapening"),
    )

    input.geometrie_wapening.zones.lb4 = LineBreak()

    input.geometrie_wapening.zones.bijlegwapening_langs_boven_diameter = NumberField(
        "Diameter bijlegwapening langsrichting boven", default=12.0, suffix="mm", flex=47, visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_langs_boven_hart_op_hart = NumberField(
        "H.o.h. afstand bijlegwapening langsrichting boven", default=150.0, suffix="mm", flex=53, visible=_bijleg_visibility
    )

    input.geometrie_wapening.zones.lb5 = LineBreak()

    # Additional reinforcement - Longitudinal bottom
    input.geometrie_wapening.zones.bijlegwapening_langs_onder_diameter = NumberField(
        "Diameter bijlegwapening langsrichting onder", default=12.0, suffix="mm", flex=47, visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_langs_onder_hart_op_hart = NumberField(
        "H.o.h. afstand bijlegwapening langsrichting onder", default=150.0, suffix="mm", flex=53, visible=_bijleg_visibility
    )

    input.geometrie_wapening.zones.lb6 = LineBreak()

    # Additional reinforcement - Transverse
    input.geometrie_wapening.zones.bijlegwapening_dwars_diameter = NumberField(
        "Diameter bijlegwapening dwarsrichting", default=12.0, suffix="mm", flex=47, visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_dwars_hart_op_hart = NumberField(
        "H.o.h. afstand bijlegwapening dwarsrichting", default=150.0, suffix="mm", flex=53, visible=_bijleg_visibility
    )

    # --- Load Zones (in belastingzones tab) ---
    input.belastingzones.info_text = Text(
        "Definieer hier de belastingzones. Elke zone wordt gestapeld vanaf één zijde van de brug. "
        "Vul alleen breedtes in voor de daadwerkelijk gedefinieerde brugsegmenten (D-nummers) "
        "onder de tab 'Dimensies'. De laatste belastingzone loopt automatisch door tot het einde van de brug; "
        "hiervoor hoeven dus geen segmentbreedtes (D-waardes) ingevuld te worden."
    )

    input.belastingzones.load_zones_array = DynamicArray(
        "Belastingzones",
        row_label="Belasting Zone",
        name="load_zones_data_array",
        default=[
            _create_default_load_zone_row(LOAD_ZONE_TYPES[0], 1.5),  # Voetgangers
            _create_default_load_zone_row(LOAD_ZONE_TYPES[1], 3.0),  # Fietsers
            _create_default_load_zone_row(LOAD_ZONE_TYPES[3], 0.5),  # Berm (new)
            _create_default_load_zone_row(LOAD_ZONE_TYPES[2], 10.5),  # Auto (Rijbaan)
        ],
    )
    input.belastingzones.load_zones_array.zone_type = OptionField("Type belastingzone", options=LOAD_ZONE_TYPES, default=LOAD_ZONE_TYPES[0])

    # Dynamically create dX_width fields for the load_zones_array
    for _idx_field in range(1, MAX_LOAD_ZONE_SEGMENT_FIELDS + 1):
        _field = NumberField(
            f"Breedte zone bij D{_idx_field}",
            default=2.0,  # Default set to 2.0m for all fields
            min=0.01,  # Minimum value set to 0.01m (1cm)
            suffix="m",
            description=f"Breedte van deze belastingzone ter hoogte van dwarsdoorsnede D{_idx_field}.",
            visible=DX_WIDTH_VISIBILITY_CALLBACKS[_idx_field],
        )
        setattr(input.belastingzones.load_zones_array, f"d{_idx_field}_width", _field)

    # --- Load Combinations (in belastingcombinaties tab) ---
    input.belastingcombinaties.permanent_factor = NumberField("Factor Permanente Belasting", default=1.35)
    input.belastingcombinaties.variable_factor = NumberField("Factor Variabele Belasting", default=1.50)

    # --- Added Pages ---
    scia = Page("SCIA")
    berekening = Page("Berekening")
    rapport = Page("Rapport", views=["get_output_report"])
