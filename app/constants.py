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
BRIDGE_DATA_PATH = PROJECT_PATH / "resources" / "data" / "bridges" / "filtered_bridges.json"

# Note: Material paths are now managed by src.common.materials module

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
# SCIA zip readme content
# ===================================================================================================================

SCIA_ZIP_README_CONTENT = """SCIA Engineer XML Files - Bridge Model

This ZIP contains the generated SCIA model files:

1. bridge_model.xml - Main model definition with geometry, materials, and mesh
2. bridge_model.def - Definition file with additional model parameters

To use these files:
1. Open SCIA Engineer (version 24.0.3015.64 or compatible)
2. Create a new project or open existing template
3. Import the XML files: File > Import > XML files
4. Review the imported model geometry and settings
5. Define load cases and run analysis as needed

Note: This is a simplified rectangular plate model. Future versions will support:
- Complex bridge geometry matching actual shape
- Variable thickness per zone
- Load cases and combinations
- Advanced material properties

Generated from VIKTOR Bridge Assessment Tool
"""

# ===================================================================================================================
# SCIA info text
# ===================================================================================================================

SCIA_INFO_TEXT = """## SCIA Engineer Integration

Deze pagina toont een preview van het SCIA model en biedt download opties voor SCIA Engineer bestanden.

### Model Informatie
Het huidige model is een **vereenvoudigde rechthoekige plaat** gebaseerd op:
- **Lengte**: Som van alle segment lengtes (Afstand tot vorige snede)
- **Breedte**: Breedte van het eerste segment (bz1 + bz2 + bz3)
- **Dikte**: Vast op 0.5m (moet nog uitgebreid worden met variabele dikte per zone)
- **Materiaal**: Standaard beton C30/37

### Materiaal Compatibiliteit
SCIA Engineer ondersteunt een brede range aan materialen via string-gebaseerde namen:

**Volledig ondersteund:**
- **Alle moderne Eurocode materialen** (C12/15 tot C90/105, B500A/B/C)
- **Oudere Nederlandse materialen** (K150-K600, B12,5-B65)
- **Oude wapeningsstaal** (QR22-QR54, QRn32-QRn54, FeB 220/400/500)
- **Historische staalsoorten** (St. 37, St. 52, Speciaal st. 36/48)

**Voordeel:** SCIA accepteert materialen direct zoals ze in de project database staan.

### Download Opties
Gebruik de onderstaande knoppen om SCIA bestanden te downloaden:

### Toekomstige Uitbreidingen
- Complexe bruggeometrie (1:1 met werkelijke brugvorm)
- Variabele dikte per zone (dz, dz_2 parameters)
- Belastinggevallen en combinaties
- Geavanceerde materiaal eigenschappen
        """

# ===================================================================================================================
# IDEA StatiCa info text
# ===================================================================================================================

IDEA_INFO_TEXT = """## IDEA StatiCa RCS Integration

Deze pagina toont een preview van het IDEA RCS model en biedt download opties voor dwarsdoorsnede analyse.

### Model Informatie
Het huidige model is een **vereenvoudigde rechthoekige plaat** met wapening gebaseerd op:
- **Breedte**: Breedte van het eerste segment (bz1 + bz2 + bz3)
- **Dikte**: Realistische dekdikte (maximum 0.8m voor plaatanalyse)
- **Materiaal**: Standaard beton C30/37
- **Wapening**: Betonstaal B500B met diameter 12mm en onderlinge afstand 150mm
- **Bovenwapening**: Hart-op-hart afstand 150mm, betondekking 55mm
- **Onderwapening**: Hart-op-hart afstand 150mm, betondekking 55mm

### Materiaal Compatibiliteit
IDEA StatiCa ondersteunt alleen moderne Eurocode materialen:

**Direct ondersteund:**
- **B500A, B500B, B500C** (moderne Eurocode wapeningsstaal)
- **C12/15 tot C50/60** (standaard betonklassen)

**Automatische omzetting oude materialen:**
- **QR24, QR22** naar B500A (lage sterkte: 220-240 N/mm²)
- **QR30, QR40, FeB 400** naar B500B (medium sterkte: 300-400 N/mm²)  
- **QR48, FeB 500** naar B500C (hoge sterkte: 400+ N/mm²)

**Aanbeveling:** Voor exacte materiaalcontrole, selecteer direct B500A/B/C in wapeningsinstellingen.

### Download Opties
Gebruik de onderstaande knoppen om IDEA RCS bestanden te downloaden:

### Toekomstige Uitbreidingen
- T-balken en kokerprofielen
- Variabele wapeningsconfiguraties per zone
- Realistische belastinggevallen uit bruggeometrie
- Uitbreiding van materiaalintegratie met Info pagina parameters
        """
