"""Module for the Overview Bridges entity parametrization."""

from viktor.parametrization import (
    ActionButton,
    ChildEntityManager,
    Parametrization,
    Text,
)


class OverviewBridgesParametrization(Parametrization):
    """Parametrization for the Overview Bridges entity."""

    introduction = Text("This is the Overview Bridges entity. It manages the bridges in the system.")

    # ChildEntityManager linked by passing the registered entity_type_name (alias)
    bridge_manager = ChildEntityManager("Bridge")

    # Moved regenerate_button below the manager
    regenerate_button = ActionButton("(Her)genereer Bruggen", method="regenerate_bridges_action")
