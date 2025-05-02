"""Module for the Overview Bridges entity parametrization."""

from viktor.parametrization import (
    ActionButton,
    ChildEntityManager,
    Page,
    Parametrization,
    Text,
)


class OverviewBridgesParametrization(Parametrization):
    """Parametrization for the Overview Bridges entity."""

    # Define the blank Home page
    home = Page("Home")

    # Define the Bridge Overview page
    bridge_overview = Page("Bridge Overview", views=["get_map_view"])
    bridge_overview.introduction = Text("This is the Overview Bridges entity. It manages the bridges in the system.")

    # ChildEntityManager linked by passing the registered entity_type_name (alias)
    bridge_overview.bridge_manager = ChildEntityManager("Bridge")

    # Moved regenerate_button below the manager
    bridge_overview.regenerate_button = ActionButton("(Her)genereer Bruggen", method="regenerate_bridges_action")
