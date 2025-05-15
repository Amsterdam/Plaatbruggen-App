# Changelog

All notable changes to this project will be documented in this file.

Semantic versioning is used to denote different versions of this project.

## [`v0.0.5`] - 2025-05-09

### Added
- Added `wapening_buigstraal.csv` containing minimum bending radii specifications for different reinforcement bar diameters (6mm to 40mm) according to Eurocode 2.
- Added "Info" page to the `Bridge` entity, displaying a map view of the specific bridge.

### Changed
- Reorganized resources directory structure for better organization:
  - Created subdirectories for different resource types: `data/materials`, `data/bridges`, `gis`, `templates`, `styles`, `images`, and `symbols`
  - Moved material CSV files to `resources/data/materials/`
  - Moved bridge data files to `resources/data/bridges/`
  - Moved GIS files to `resources/gis/`
  - Moved document templates to `resources/templates/`
  - Moved style files to `resources/styles/`
- Renamed map view from "Kaart Huidige Brug" to "Locatie Brug" in bridge entity
- Updated bridge deck parametrization for zone 2 thickness:
  - Replaced "Extra dikte zone 2" (`dze`) with "Dikte zone 2 (`dz_2`)" to directly input total thickness.
  - Updated `model_creator.py` to use the new `dz_2` parameter for 3D model generation.
- Refactored map and geometry processing logic from `BridgeController` and `OverviewBridgesController` into a new shared utility module: `app/common/map_utils.py`.
- Updated `BridgeController` and `OverviewBridgesController` to utilize the new shared map utilities.
- Modified `BridgeController`'s `get_bridge_map_view` method to fetch `last_saved_params` using `viktor.api_v1` for improved robustness in retrieving entity parameters.
- Performed internal refactoring of `BridgeController`'s `get_bridge_map_view` and related helper methods to enhance structure and address linter warnings.
- Simplified shapefile path retrieval in `BridgeController` by inlining the `_get_shapefile_path` helper method into `get_bridge_map_view`.
- Centralized individual bridge shapefile loading and filtering by moving logic from `BridgeController`._load_and_filter_geodataframe` to a new `load_and_filter_bridge_shapefile` function in `app/common/map_utils.py`.

### Fixed
- Resolved issues where `OBJECTNUMM` was not found in `Bridge` entity parameters by:
    - Moving hidden `TextField` parameters (`bridge_objectnumm`, `bridge_name`) into the newly created "Info" page.
    - Updating parameter access in `BridgeController` to `params.info.bridge_objectnumm`.
- Addressed `AttributeError: info` for older `Bridge` entities by:
    - Making parameter access in `BridgeController` more robust using `params.get("info")`.
    - Updating `OverviewBridgesController` (`_create_missing_children` method) to correctly structure parameters under an "info" key when creating new bridge entities.
- Corrected various Ruff linter errors in `BridgeController` and `app/common/map_utils.py`, including `ERA001` (commented-out code), `TRY301` (abstract `raise`), `C901`/`PLR0911`/`PLR0912` (complexity/branches/returns), `TRY300` (consider `else`), `W293` (whitespace), `RUF013` (implicit `Optional`), `ANN202` (missing return type), and `RET505` (unnecessary `else`).


## [`v0.0.4`] - 2025-05-08

### Added
- Added `betonkwaliteit.csv` containing concrete quality specifications with strength parameters
- Added `betonstaalkwaliteit.csv` containing reinforcement steel quality specifications with yield and design strengths
- Added `voorspanstaalkwaliteit.csv` containing prestressing steel quality specifications with strength and allowable stress parameters
- Added an explanatory text field for the bridge segments in the parametrization.

### Changed
- Set default of two items for the bridge segments dynamic array.
- Enhanced the 2D top view (`create_2d_top_view` in `src/geometry/model_creator.py`) to include:
    - Clear visual separation of bridge zones (1, 2, and 3) for each segment.
    - Background coloring for each zone to improve visual distinction.
    - Detailed dimension labels for segment lengths (`l`) and zone widths (`bz1`, `bz2`, `bz3`) at each cross-section.
    - Identifier labels (e.g., "D1", "D2") for each cross-section.
    - Zone numbering within each segment (e.g., "1-1", "2-1", "3-1").

### Fixed
- Corrected visibility logic for "Afstand tot vorige snede" field in the bridge dimensions dynamic array, ensuring it is hidden for the first segment.
- Suppressed a `DeprecationWarning` from `geopandas._compat` related to `shapely.geos` to keep console output clean. This is an internal `geopandas` issue and does not affect functionality.

## [`v0.0.3`] - 2025-05-08

### Added
- Viktor CI/CD pipeline
- Home page with documentation view
- More detailed README content including Usage, Technologies, and Contribution guidelines.
- Link to live VIKTOR application in README.
- Hover effect on changelog version sections.
- Set `OverviewBridges` entity as the default start page for the application.
- Implemented 3D visualization of bridge geometry based on parametrized dimensions.
- Added dynamic 2D views: top view, longitudinal section, and cross-section, derived from the 3D model.
- Introduced detailed parametrization for bridge entities, including:
    - Multi-section bridge dimensions using a dynamic array.
    - Reinforcement geometry parameters.
    - Load zone definitions and intensities.
    - Load combination factors.
    - Controls for section view locations.
- Added placeholder pages for SCIA integration, Calculation, and Reporting within the bridge entity.

### Fixed
- Initial configuration issues
- Pre-commit configuration to correctly install `types-Markdown` and `types-shapely` for `mypy` hook.
- Corrected developer installation instructions in README.
- Corrected contact email format in README.
- `ARG002` VIKTOR view signature conflict with Ruff.

### Changed
- Updated documentation structure
- Improved styling for README and Changelog view (layout, spacing, typography, colors).
- Restructured README for better user/developer audience separation.
- Clarified contribution workflow distinction (internal vs. external).

## [`v0.0.2`] - 2025-05-01

### Added
- Initial release
- Basic bridge data visualization
- Integration with map services

### Fixed
- Development environment setup

### Changed
- Initial project structure

## [`v0.0.1`] - 2025-05-01

