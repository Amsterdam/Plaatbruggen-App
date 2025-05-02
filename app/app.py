"""Main application definition module."""

from pathlib import Path

from viktor_app.batch_controller import BatchController

from viktor.core import ViktorApplication


class Application(ViktorApplication):
    """
    Automatisch Toetsmodel voor Plaatbruggen.

    Deze applicatie maakt het mogelijk om meerdere betonnen plaatbruggen
    te modelleren, analyseren met SCIA Engineer, en toetsen volgens Eurocode.
    """

    name = "Automatisch Toetsmodel Plaatbruggen"
    version = "0.0.1"
    controller = BatchController
    path = Path(__file__).parent
