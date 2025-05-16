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
