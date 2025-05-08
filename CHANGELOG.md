# Changelog

All notable changes to this project will be documented in this file.

Semantic versioning is used to denote different versions of this project.

## [`v0.0.5`] - 2025-05-08

### Fixed
- Suppressed a `DeprecationWarning` from `geopandas._compat` related to `shapely.geos` to keep console output clean. This is an internal `geopandas` issue and does not affect functionality.

## [`v0.0.4`] - 2025-05-08

### Added
- Added `betonkwaliteit.csv` containing concrete quality specifications with strength parameters
- Added `betonstaalkwaliteit.csv` containing reinforcement steel quality specifications with yield and design strengths
- Added an explanatory text field for the bridge segments in the parametrization.

### Changed
- Set default of two items for the bridge segments dynamic array.

### Fixed
- Corrected visibility logic for "Afstand tot vorige snede" field in the bridge dimensions dynamic array, ensuring it is hidden for the first segment.

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

