# Automatisch Toetsmodel Plaatbruggen

## Beschrijving

Deze applicatie, draaiend op het VIKTOR-platform, voert geautomatiseerde structurele toetsingen uit voor plaatbruggen. Het model analyseert bruggegevens en past relevante technische normen en berekeningen toe om de constructieve veiligheid en prestaties te beoordelen.

Als u deze documentatie op GitHub bekijkt, kunt u de live productie-applicatie [hier](https://amsterdam.viktor.ai/workspaces/108/app/dashboard) vinden.

*Toegang tot deze omgeving is beperkt. Neem contact op met Quincy de Klerk (q.klerk@amsterdam.nl) of een andere beheerder voor toegangsrechten.*

## Gebruik

De applicatie biedt de volgende functionaliteiten:

-   **Overzicht Bruggen Pagina:** Navigeer hierheen voor een overzicht van alle bruggen die beschikbaar zijn om door te rekenen.
-   **Batch Berekening Pagina:** Navigeer naar deze pagina om in één klik alle (geselecteerde) bruggen te berekenen en de status hiervan te volgen.
-   **Resultaten Pagina:** Navigeer naar deze pagina om de eindresultaten van de berekeningen in te zien.

*Elke pagina bevat meer gedetailleerde informatie en specifieke functionaliteiten.*

## Contact
**Gemaakt & Gepubliceerd op VIKTOR door:**

- Quincy de Klerk - (q.klerk@amsterdam.nl)
- Geert Vos - (geert.vos@amsterdam.nl)
- Rahman Özdemir - (rahman.ozdemir@arcadis.com)
- Paul Wensveen - (paul.wensveen@arcadis.com)
- Theresa Höfker - (theresa.hofker@arcadis.com)
- Jona Rens - (jona@epicpeople.nl)

**Ontwikkelteam:**
- **Ctrl+B**

---

## Voor Ontwikkelaars

### Vereisten

**Installeer Viktor & Python:**
https://docs.viktor.ai/docs/getting-started/installation/

### App-installatie (Lokale Ontwikkeling)

Voor het lokaal ontwikkelen en draaien van deze applicatie:

1.  **Kloon de repository:**
    ```bash
    git clone https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen.git
    cd automatisch-toetsmodel-plaatbruggen
    ```
2.  **Zorg dat de [VIKTOR Command Line Interface (CLI)](https://docs.viktor.ai/docs/getting-started/installation/) geïnstalleerd en geconfigureerd is.**
3.  **Start de applicatie vanuit de repository directory:**
    ```bash
    viktor-cli install
    viktor-cli start
    ```
    De CLI zal de benodigde dependencies installeren en de app starten in uw lokale ontwikkelomgeving.

### Technologieën

-   [VIKTOR Platform](https://www.viktor.ai/)
-   Python 3.12
-   GeoPandas (voor GIS data)
-   Shapely (voor geometrische operaties)
-   Plotly (voor visualisaties)

*Voor de volledige lijst van runtime dependencies, zie [`requirements.txt`](requirements.txt).*

### Bijdragen

Interne medewerkers (@amsterdam.nl) met toegang tot de Amsterdam organisatie op GitHub volgen de standaard workflow:

1.  **Kloon de repository:**
    ```bash
    git clone https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen.git
    cd automatisch-toetsmodel-plaatbruggen
    ```
2.  **Zorg dat je lokale `development` branch up-to-date is:**
    ```bash
    git checkout development
    git pull origin development
    ```
3.  **Maak een feature branch aan** vanuit `development` (bijv. `git checkout -b <issue-nummer>_<korte-beschrijving>`).
4.  **Implementeer je wijzigingen** en commit regelmatig (`git commit -m "Duidelijke message"`).
5.  **Push je feature branch** naar de `origin` remote (`git push origin <naam-feature-branch>`).
6.  **Maak een Pull Request aan** op GitHub van jouw feature branch naar de `development` branch.

*Externe medewerkers volgen de uitgebreide **fork & pull request workflow** zoals beschreven in [docs/tijdelijke git development workflow.md](docs/tijdelijke%20git%20development%20workflow.md).*

Voor het melden van bugs of het voorstellen van features, gebruik de [GitHub Issues](https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen/issues).

### Licentie

Dit project is gelicentieerd onder de [European Union Public Licence v. 1.2 (EUPL v. 1.2)](LICENSE).
