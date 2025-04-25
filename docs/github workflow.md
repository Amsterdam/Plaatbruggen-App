# GitHub Issue Workflow

Deze workflow beschrijft hoe we omgaan met issues in de GitHub repository.

1.  **Issue Aanmaken:**
    *   Maak een issue aan voor elke nieuwe taak, bug, of feature request.
    *   Geef de issue een duidelijke titel en beschrijving.
    *   Voeg relevante labels toe (e.g., `bug`, `feature`, `documentation`).

2.  **Starten met een Issue:**
    *   Wijs de issue aan jezelf toe (assignee) of laat een comment achter dat je ermee aan de slag gaat.

3.  **Branch Aanmaken (vanuit de Issue, kan alleen door @amsterdam.nl accounts):**
    *   Navigeer naar de issue op GitHub.
    *   In de rechterkolom, onder "Development", klik op "Create a branch". 
    *   GitHub stelt een branch naam voor (meestal `<issue-nummer>-<issue-titel>`). Pas deze eventueel aan volgens de conventie (`<story-nummer>_<korte_beschrijving>`) indien nodig.
    *   Zorg ervoor dat de branch wordt aangemaakt vanuit de `development` branch.
    *   Kies ervoor om de branch in je **eigen fork** aan te maken.


4.  **Werken in de Branch en Pull Requests:**
    *   Zie [tijdelijke git workflow.md](tijdelijke%20git%20workflow.md) voor de volledige instructies over het werken met branches en pull requests.

6.  **Reageren op de Issue:**
    *   Plaats een commentaar op de oorspronkelijke GitHub issue met een link naar de Pull Request die je hebt aangemaakt. Dit houdt iedereen op de hoogte.
    *   Je kunt ook direct vanuit de PR naar de issue linken.

7.  **Code Review en Merge:**
    *   Een beheerder (zoals Quincy) controleert de Pull Request (code review).
    *   Indien akkoord, wordt de PR gemerged in de `development` branch van de `Amsterdam` repository.
    *   De beheerder sluit de issue (als dit niet automatisch gebeurde door de `Closes #...` tag in de PR).

8.  **Opruimen (Optioneel):**
    *   Na het mergen van de PR, kun je de feature branch verwijderen uit je fork en lokaal. 