"""Constants used throughout the application."""
# ===================================================================================================================
# Imports
# ===================================================================================================================

from pathlib import Path

# ===================================================================================================================
# Paths
# ===================================================================================================================

PROJECT_PATH = Path(__file__).parent.parent
README_PATH = PROJECT_PATH / "README.md"
CHANGELOG_PATH = PROJECT_PATH / "CHANGELOG.md"
CSS_PATH = PROJECT_PATH / "resources" / "styles" / "style.css"
OUTPUT_REPORT_PATH = PROJECT_PATH / "resources" / "templates" / "template_eindrapport.docx"
REINFORCEMENT_PATH = PROJECT_PATH / "resources" / "data" / "materials" / "betonstaalkwaliteit.csv"

# ===================================================================================================================
# Docs - Readme
# ===================================================================================================================

README_CONTENT = """
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
    }

    .container {
        display: flex;
        height: 100%;
    }

    .iframe-wrapper {
        flex: 1;
        margin: 10px;
        border: none;
    }

    .iframe {
        width: 100%;
        height: 100%;
        border: none;
    }

        </style>
    </head>
    <body>
        <div class="container">
        <div class="iframe-wrapper">
"""

# ===================================================================================================================
# Parametrization Constants
# ===================================================================================================================

MAX_LOAD_ZONE_SEGMENT_FIELDS = 15  # Define how many D-fields (D1 to D15) we'll support for load zones
LOAD_ZONE_TYPES = ["Voetgangers", "Fietsers", "Auto", "Berm"]


# ===================================================================================================================
# Tables from codes
# ===================================================================================================================

# Combination table according to NEN-EN 1990 table NB.19
#
# Legend:
# X = Leading action     x = Included in combination     0 = Not included in combination
#
COMBINATION_TABLE = {
    "Perm": {
        "Permanente belasting": "X",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "",
        "UDL": "",
        "Enkele as": "",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Perm zet": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "X",
        "TS": "",
        "UDL": "",
        "Enkele as": "",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr1a": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "X",
        "UDL": "X",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "x",
        "Wind Fw*": "x",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr1b": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "",
        "UDL": "",
        "Enkele as": "X",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr2": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "X",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "x",
        "Wind Fw*": "x",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr3": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "",
        "UDL": "",
        "Enkele as": "",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "X",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr4": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "",
        "UDL": "",
        "Enkele as": "",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "X",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "gr5": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "X",
        "Wind Fwk": "x",
        "Wind Fw*": "x",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Wind gr1a": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "X",
        "Wind Fw*": "",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Wind gr2": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "X",
        "Wind Fw*": "",
        "Temperatuur": "x",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Temp gr1": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "x",
        "Wind Fw*": "",
        "Temperatuur": "X",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Temp gr2": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "x",
        "Wind Fw*": "",
        "Temperatuur": "X",
        "Sneeuw": "",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Sneeuw": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "",
        "UDL": "",
        "Enkele as": "",
        "Horizontale belasting": "",
        "Fiets- en voetpaden": "",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "X",
        "Impact op of onder de brug": "",
        "Aardbevingsbelasting": "",
    },
    "Aanrijding gr1a": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "X",
        "Aardbevingsbelasting": "",
    },
    "Aanrijding gr2": {
        "Permanente belasting": "x",
        "Voorspaning": "x",
        "Zetting": "",
        "TS": "x",
        "UDL": "x",
        "Enkele as": "",
        "Horizontale belasting": "x",
        "Fiets- en voetpaden": "x",
        "Mensenmenigte": "",
        "Bijzonder voertuigen": "",
        "Wind Fwk": "",
        "Wind Fw*": "",
        "Temperatuur": "",
        "Sneeuw": "",
        "Impact op of onder de brug": "X",
        "Aardbevingsbelasting": "",
    },
}
