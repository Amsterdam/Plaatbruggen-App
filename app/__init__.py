"""viktor."""

__version__ = "0.0.1"

# Viktor app package for Automatisch Toetsmodel Plaatbruggen

from viktor import InitialEntity  # type: ignore[attr-defined]

from .bridge.controller import BridgeController as Bridge  # Uncommented Bridge import

# from .simple_controller import SimpleController # Old import
from .overview_bridges.controller import OverviewBridgesController as OverviewBridges  # New import

# Import the controllers. The 'as' part defines the entity_type_name used in InitialEntity

# --- IMPORTANT NOTE (VIKTOR SDK v14 Compatibility) ---
# The 'InitialEntity' class below is deprecated in SDK v14+ and should ideally
# be replaced by assigning a list of dictionaries directly to 'viktor.initial_entities'.
# Example recommended format:
# viktor.initial_entities = [
#     {"entity_type_name": "OverviewBridges", "is_initial_entity": True},
# ]
# However, attempts to use the recommended format resulted in persistent runtime errors:
# "App specification is invalid: You should provide at least 1 top level entity when using tree app type."
# This occurred despite correct syntax and environment restarts (SDK 14.20.0, Connector 6.4.0).
# Therefore, the deprecated 'InitialEntity' is used here as a temporary workaround.
# The MyPy error for the 'InitialEntity' import is suppressed above using '# type: ignore[attr-defined]'.
# This situation should be revisited if the SDK or connector is updated.
# --- END NOTE ---

initial_entities = [
    InitialEntity(
        entity_type_name="OverviewBridges",  # Use the alias
        name="Overzicht Bruggen",  # Updated name
        children=[],
    )
]
