"""viktor."""

__version__ = "0.0.1"

# Viktor app package for Automatisch Toetsmodel Plaatbruggen

from viktor import InitialEntity

from .bridge.controller import BridgeController as Bridge

# Import the controllers. The 'as' part defines the entity_type_name used in InitialEntity
from .overview_bridges.controller import OverviewBridgesController as OverviewBridges

initial_entities = [
    InitialEntity(
        entity_type_name="OverviewBridges",
        name="Overzicht Bruggen",
        children=[
            InitialEntity(entity_type_name="Bridge", name="Voorbeeld Brug 1", children=[]),
            InitialEntity(entity_type_name="Bridge", name="Voorbeeld Brug 2", children=[]),
        ],
    )
]
