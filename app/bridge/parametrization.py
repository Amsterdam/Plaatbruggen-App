"""Module for the Bridge entity parametrization."""

from viktor.parametrization import NumberField, Parametrization


class BridgeParametrization(Parametrization):
    """Parametrization for the individual Bridge entity."""

    # --- Bridge Geometry ---
    lengte = NumberField("Lengte", default=10.0, suffix="m")
    breedte = NumberField("Breedte", default=5.0, suffix="m")
