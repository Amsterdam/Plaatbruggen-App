# Project Architectuur: automatisch-toetsmodel-plaatbruggen

Dit document beschrijft de voorgestelde architectuur voor de VIKTOR-applicatie gericht op geautomatiseerde brugberekeningen, met inzichten uit de conceptdocumentatie (v1, jan 2025).

## Doelstellingen

*   Scheiden van de kernberekeningslogica van de VIKTOR-interfacelaag.
*   Zorgen voor hoge testbaarheid van de kernlogica.
*   Bevorderen van onderhoudbaarheid en schaalbaarheid voor een complexe applicatie.
*   Potentieel hergebruik van de kernlogica met andere interfaces in de toekomst mogelijk maken.
*   Faciliteren van bulktesten van meerdere bruggen middels een parent/child-structuur.

## Voorgestelde Mapstructuur

```
automatisch-toetsmodel-plaatbruggen/
├── app/                     # VIKTOR applicatiepakket (Interface Laag), georganiseerd per feature/entiteit
│   ├── overview_bridges/   # Logica voor de batch calculatie entiteit
│   │   ├── controller.py      # Controller & Views
│   │   ├── parametrization.py
│   │   └── utils.py (optioneel)
│   ├── bridge/              # Logica voor de individuele brug entiteit
│   │   ├── controller.py      # Controller & Views
│   │   ├── parametrization.py
│   │   └── utils.py (optioneel)
├── src/                     # Kern berekening/logica pakket (Backend/Domein Laag) - GEEN VIKTOR IMPORTS
│   ├── bridge_analysis/     # Hoofdlogica voor brugberekeningen
│   │   ├── calculators/     # Modules voor specifieke berekeningstypen
│   │   │   ├── load_calculator.py   # Behandelt permanente, verkeers- (LM1, UDL/TS), temp lasten (H5.4)
│   │   │   ├── check_calculator.py  # Behandelt wapenings- & dwarskrachttoetsen (H6)
│   │   │   └── ...                # Andere specifieke calculators indien nodig
│   │   ├── models/          # Datastructuren (Pydantic aanbevolen)
│   │   │   ├── bridge_model.py    # Representeert bruggeometrie, materialen, zones
│   │   │   ├── load_model.py      # Representeert belastinggevallen, combinaties
│   │   │   └── result_model.py    # Representeert berekenings-/toetsingsresultaten
│   │   ├── types/           # Logica specifiek voor verschillende brugtypen (Type 0-3, H2)
│   │   │   ├── plate_bridge_base.py # Basis klasse/logica?
│   │   │   └── ...                # Type-specifieke implementaties
│   │   └── utils.py         # Utility functies voor analyse (bv. geometrie helpers)
│   ├── common/              # Gedeelde utilities/modellen over verschillende src/ modules
│   │   └── ...                # Gedeelde code
│   ├── integrations/        # Logica voor interactie met externe software
│   │   └── scia_interface.py  # Behandelt SCIA interactie
│   ├── constants/           # Gedeelde configuratie data
│   │   └── materials.json     # Standaard materiaaleigenschappen (Tabel 1-3)
│   └── ...
├── tests/                   # Unit- en integratietests
│   ├── test_app/            # Tests voor de app-laag (VIKTOR layer)
│   └── test_src/            # Unit tests voor de kernlogica (hoge prioriteit)
│       ├── test_bridge_analysis/
│       │   ├── test_calculators/
│       │   │   └── ...
│       │   ├── test_models/
│       │   │   └── ...
│       │   └── test_integrations/
│       │       └── test_scia_interface.py
│       └── ...
├── doc/                     # Documentatie map
│   └── architecture.md      # Dit bestand
├── viktor.config.toml       # VIKTOR app configuratie
├── requirements.txt         # Productie dependencies (viktor, numpy, scipy, pandas, etc.)
├── requirements_dev.txt     # Ontwikkeling dependencies (pytest, ruff, mypy, etc.)
├── pyproject.toml           # Build systeem en tool configuratie
├── .pre-commit-config.yaml  # Pre-commit hooks configuratie
├── .ruff.toml               # Ruff linter/formatter configuratie
├── .gitignore               # Git ignore regels
└── README.md                # Project beschrijving, setup instructies
```

## Laag Beschrijvingen en Werkwijze

1.  **`app/` (VIKTOR Laag):**
    *   Bevat alle VIKTOR SDK gerelateerde code, georganiseerd in submappen per feature of entiteit type (bv. `app/overview_bridges/`, `app/bridge/`).
    *   Elke submap bevat typisch:
        *   `parametrization.py`: Definieert de gebruikersinterface voor die feature/entiteit.
        *   `controller.py`: Orkestreert de workflow, definieert VIKTOR views en roept `src/` logica aan.
        *   Optioneel `utils.py` voor UI-specifieke helpers.
    *   Controllers (`app/.../controller.py`) beheren de interactie:
        *   Beheren VIKTOR entiteiten (bv. parent/child voor batch/bridge).
        *   Halen gebruikersinvoer op via `params` (gedefinieerd in `parametrization.py`).
        *   Halen configuraties op uit `src/constants/`.
        *   Roepen de kernlogica in `src/` aan.
        *   Verwerken resultaten uit `src/`.
        *   Genereren VIKTOR views (gedefinieerd binnen de controller zelf).
        *   Genereren potentieel PDF-rapporten (m.b.v. `utils.py` of direct in controller).

2.  **`src/` (Kern Logica Laag):**
    *   **Geen VIKTOR SDK imports toegestaan.** Bevat pure, herbruikbare Python logica.
    *   `bridge_analysis/`: Kern domeinlogica voor constructieve analyse en toetsen, volgens Eurocodes en specifieke richtlijnen (NEN 8700 serie, RBK, TAB).
        *   `calculators/`: Implementeert specifieke berekeningsstappen (lasten, toetsen).
        *   `models/`: Definieert duidelijke datacontracten voor intern gebruik en communicatie tussen lagen (Pydantic aanbevolen).
        *   `types/`: Behandelt variaties tussen verschillende brugtypen (Type 0-3).
    *   `integrations/`: Interfaces met externe tools.
        *   `scia_interface.py`: Beheert het gedetailleerde proces van het genereren van SCIA input XML, gebruik van template bestanden, uitvoeren van SCIA (mogelijk via `ESA_XML.exe`), en parsen van resultaten.
        *   *(Toekomst)* `idea_interface.py` kan hier worden toegevoegd als gedetailleerde doorsnedetoetsen met IDEA StatiCa later nodig zijn.
    *   `constants/`: Biedt toegang tot gedeelde, niet-gebruikersspecifieke data zoals standaard materialen geladen uit JSON/YAML bestanden.
    *   `common/`: Algemene utility functies.

3.  **`tests/` (Test Laag):**
    *   `test_src/`: Hoge prioriteit unit tests die de correctheid verifiëren van calculators, modellen, type-specifieke logica, en integratiecomponenten (bv. SCIA input generatie).
    *   `test_app/`: Lagere prioriteit tests voor UI helpers (`app/.../utils.py`) of potentieel integratietests voor de VIKTOR controllers (`app/.../controller.py`).

## Voordelen

*   **Duidelijke Scheiding:** Isoleert VIKTOR-specifieke zaken, maakt kernlogica herbruikbaar en onafhankelijk testbaar.
*   **Testbaarheid:** `src/` is gemakkelijk unit-testbaar.
*   **Onderhoudbaarheid:** Structuur sluit aan bij het domein, vereenvoudigt updates en debuggen.
*   **Schaalbaarheid:** Modulair ontwerp ondersteunt toevoegen van nieuwe brugtypen, berekeningen of externe tool integraties.

## Belangrijke Overwegingen

*   **Data Overdracht:** Gebruik goed-gedefinieerde Pydantic modellen (`src/models/`) voor robuuste data-uitwisseling tussen `app` en `src`.
*   **Configuratie Beheer:** Gebruik `src/constants/` voor gedeelde data, onderscheiden van gebruikersinvoer beheerd door VIKTOR.
*   **Interactie Externe Tool:** Encapsuleer alle SCIA-specifieke logica binnen `src/integrations/scia_interface.py`. Behandel potentiële fouten tijdens bestandsgeneratie, executie of parsen.
*   **Rapportage:** Plan hoe de `app` laag (specifiek controllers/utils) data verzamelt van `src` resultaten en de vereiste PDF rapporten genereert.
*   **Bulk Verwerking:** Ontwerp de controller in `app/overview_bridges/controller.py` om efficiënt child (`app/bridge/`) entiteiten te beheren en resultaten te aggregeren.
*   **Foutafhandeling:** Implementeer robuuste foutafhandeling door de gehele applicatie, speciaal voor interacties met externe tools en bestandsoperaties. 