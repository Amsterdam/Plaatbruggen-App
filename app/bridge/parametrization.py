"""Module for the Bridge entity parametrization."""

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


def calculate_max_array(params: object) -> int:
    """Calculate the maximum number of reinforcement zones based on the number of bridge segments."""
    sections = len(params.bridge_segments_array)
    return 3 * (sections - 1)

def define_options_numbering(params: object) -> list:
    """
    Define options for zone numbering based on the number of segments.

    Args:
        params: Parameters containing bridge_segments_array

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
        views=["get_top_view", "get_3d_view",
               "get_2d_horizontal_section",
               "get_2d_longitudinal_section",
               "get_2d_cross_section"],
    )

    ###############################################
    ## Invoer Page
    ##############################################

    # --- Tabs within Invoer Page ---
    input.dimensions = Tab("Dimensies")
    input.geometrie_wapening = Tab("Wapening")
    input.belastingzones = Tab("Belastingzones")
    input.belastingcombinaties = Tab("Belastingcombinaties")

    #----------------------------------------
    ## Dimensions tab
    #----------------------------------------

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
        "Doorsnede bovenaanzicht z =",
        default=-1.0,
        suffix="m",
        visible=Lookup("input.dimensions.toggle_sections")
    )
    input.dimensions.longitudinal_section_loc = NumberField(
        "Doorsnede langsdoorsnede y =",
        default=0.0,
        suffix="m",
        visible=Lookup("input.dimensions.toggle_sections")
    )
    input.dimensions.cross_section_loc = NumberField(
        "Doorsnede dwarsdoorsnede x =",
        default=0.0,
        suffix="m",
        visible=Lookup("input.dimensions.toggle_sections")
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
    )    # General reinforcement parameters
    input.geometrie_wapening.staalsoort = OptionField(
        "Staalsoort",
        options=get_steel_qualities(),
        default="B500B",  # Changed to more modern default
        description="De kwaliteit van het betonstaal dat wordt toegepast in de brug."
    )

    input.geometrie_wapening.dekking = NumberField(
        "Betondekking",
        default=55.0,
        suffix="mm",
        description="De betondekking is de afstand tussen de buitenkant van het beton en de buitenste wapeningslaag."
    )
    input.geometrie_wapening.langswapening_buiten = BooleanField(
        "Langswapening aan buitenzijde?",
        default=True,
        description=(
            "Indien aangevinkt ligt de langswapening aan de buitenzijde van het beton. "
            "Indien uitgevinkt ligt de dwarswapening aan de buitenzijde."
        )
    )

    input.geometrie_wapening.zones = DynamicArray(
        "Wapening per zone",
        min=3,
        max=calculate_max_array,
        name="reinforcement_zones_array",
        default= [{
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
        ]
    )

    # Zone number display
    input.geometrie_wapening.zones.zone_number = OptionField(
        "Zone nummer",
        options=define_options_numbering,
        description="Dit is het zone nummer dat correspondeert met de zone in de brug."
    )

    input.geometrie_wapening.zones.lb1 = LineBreak()

    # Main reinforcement - Longitudinal top
    input.geometrie_wapening.zones.hoofdwapening_langs_boven_diameter = NumberField(
        "Diameter hoofdwapening langsrichting boven", default=12.0, suffix="mm"
    )
    input.geometrie_wapening.zones.hoofdwapening_langs_boven_hart_op_hart = NumberField(
        "Hart-op-hart afstand hoofdwapening langsrichting boven", default=150.0, suffix="mm"
    )
    input.geometrie_wapening.zones.lb2 = LineBreak()

    # Main reinforcement - Longitudinal bottom
    input.geometrie_wapening.zones.hoofdwapening_langs_onder_diameter = NumberField(
        "Diameter hoofdwapening langsrichting onder", default=12.0, suffix="mm"
    )
    input.geometrie_wapening.zones.hoofdwapening_langs_onder_hart_op_hart = NumberField(
        "Hart-op-hart afstand hoofdwapening langsrichting onder", default=150.0, suffix="mm"
    )
    input.geometrie_wapening.zones.lb3 = LineBreak()

    # Main reinforcement - Transverse
    input.geometrie_wapening.zones.hoofdwapening_dwars_diameter = NumberField(
        "Diameter hoofdwapening dwarsrichting", default=12.0, suffix="mm"
    )
    input.geometrie_wapening.zones.hoofdwapening_dwars_hart_op_hart = NumberField(
        "Hart-op-hart afstand hoofdwapening dwarsrichting", default=150.0, suffix="mm"
    )

    # Visual separator for bijlegwapening
    input.geometrie_wapening.zones.separator1 = LineBreak()

    # Additional reinforcement toggle
    input.geometrie_wapening.zones.heeft_bijlegwapening = BooleanField(
        "Bijlegwapening aanwezig?", default=False
    )

    # Additional reinforcement fields - only visible when heeft_bijlegwapening is True
    _bijleg_visibility = DynamicArrayConstraint(
        dynamic_array_name="reinforcement_zones_array",
        operand=Lookup("$row.heeft_bijlegwapening"),
    )

    input.geometrie_wapening.zones.lb4 = LineBreak()

    input.geometrie_wapening.zones.bijlegwapening_langs_boven_diameter = NumberField(
        "Diameter bijlegwapening langsrichting boven", default=12.0, suffix="mm", visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_langs_boven_hart_op_hart = NumberField(
        "Hart-op-hart afstand bijlegwapening langsrichting boven", default=150.0, suffix="mm", visible=_bijleg_visibility
    )

    input.geometrie_wapening.zones.lb5 = LineBreak()

    # Additional reinforcement - Longitudinal bottom
    input.geometrie_wapening.zones.bijlegwapening_langs_onder_diameter = NumberField(
        "Diameter bijlegwapening langsrichting onder", default=12.0, suffix="mm", visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_langs_onder_hart_op_hart = NumberField(
        "Hart-op-hart afstand bijlegwapening langsrichting onder", default=150.0, suffix="mm", visible=_bijleg_visibility
    )

    input.geometrie_wapening.zones.lb6 = LineBreak()

    # Additional reinforcement - Transverse
    input.geometrie_wapening.zones.bijlegwapening_dwars_diameter = NumberField(
        "Diameter bijlegwapening dwarsrichting", default=12.0, suffix="mm", visible=_bijleg_visibility
    )
    input.geometrie_wapening.zones.bijlegwapening_dwars_hart_op_hart = NumberField(
        "Hart-op-hart afstand bijlegwapening dwarsrichting", default=150.0, suffix="mm", visible=_bijleg_visibility
    )

    # --- Load Zones (in belastingzones tab) ---
    input.belastingzones.zone_breedte = NumberField("Zone Breedte", default=1.0, suffix="m")
    input.belastingzones.load_intensity = NumberField("Belasting Intensiteit", default=5.0, suffix="kN/m²")

    # --- Load Combinations (in belastingcombinaties tab) ---
    input.belastingcombinaties.permanent_factor = NumberField("Factor Permanente Belasting", default=1.35)
    input.belastingcombinaties.variable_factor = NumberField("Factor Variabele Belasting", default=1.50)

    # --- Added Pages ---
    scia = Page("SCIA")
    berekening = Page("Berekening")
    rapport = Page("Rapport", views="get_output_report")
