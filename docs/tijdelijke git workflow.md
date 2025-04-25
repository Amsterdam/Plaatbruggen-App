## 🔄 Workflow voor samenwerking (Fork & Pull Request)

Omdat de repository openbaar is en sommige teamleden (nog) geen toegang hebben tot de organisatie, gebruiken we een **fork-based workflow**. Volg de stappen hieronder om samen te werken aan deze repository.

### 1. Fork de repository
Ga naar [https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen](https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen)  
Klik rechtsboven op **"Fork"** en kies je eigen GitHub-account.

### 2. Clone je fork lokaal
```bash
git clone https://github.com/<jouw-gebruikersnaam>/automatisch-toetsmodel-plaatbruggen.git
cd automatisch-toetsmodel-plaatbruggen
```

### 3. Voeg de originele repo toe als upstream
```bash
git remote add upstream https://github.com/Amsterdam/automatisch-toetsmodel-plaatbruggen.git
```

### 4. Blijf up-to-date met de hoofdrepo 
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 5. Starten met een nieuwe taak/feature (nadat je al geforked hebt)

Als je al een fork hebt en de `upstream` remote correct is ingesteld, volg dan deze stappen om aan een *nieuwe* feature branch te beginnen die via een GitHub Issue is aangemaakt in de `Amsterdam` repository:

1.  **Update je lokale `development` branch:** Zorg dat je lokale `development` branch gelijk is aan die van `upstream`.
    ```bash
    git checkout development
    git fetch upstream
    git merge upstream/development
    # Optioneel, maar aanbevolen: update ook de development branch op je eigen fork (origin)
    git push origin development
    ```
2.  **Haal de nieuwe feature branch op van `upstream`:**
    ```bash
    git fetch upstream
    ```
3.  **Checkout de feature branch lokaal:**
    ```bash
    # Vervang <naam-van-de-feature-branch> door de daadwerkelijke naam
    git checkout <naam-van-de-feature-branch>
    # Bijvoorbeeld: git checkout 73822_korte_taak_beschrijving
    ```
4.  **Begin met werken:**
    Je bent nu op de juiste branch. Maak je wijzigingen.
    ```bash
    # Maak wijzigingen...
    git add .
    git commit -m "Beschrijvende commit message"
    ```
5.  **Push naar je fork (`origin`):**
    De *eerste keer* dat je pusht voor deze nieuwe branch, moet je expliciet aangeven dat je naar je eigen fork (`origin`) wilt pushen en de tracking instellen:
    ```bash
    # Vervang <naam-van-de-feature-branch> door de daadwerkelijke naam
    git push --set-upstream origin <naam-van-de-feature-branch>
    ```
    Voor alle volgende pushes op deze branch kun je simpelweg `git push` gebruiken.

### 6. Werk op een eigen branch (Algemene commit/push workflow)

Nadat je de branch hebt uitgecheckt (volgens stap 3 of 5), werk je als volgt:
```bash
# Voer je wijzigingen door
git add .
git commit -m "Duidelijke commit message"
git push # Push naar je fork (origin)
```

### 7. Maak een Pull Request aan
Ga naar je fork op GitHub en klik op **"Compare & pull request"**
Kies `Amsterdam/automatisch-toetsmodel-plaatbruggen:development` als doelbranch (base).
Kies jouw feature branch in je fork als bronbranch (compare).
Beschrijf duidelijk wat je hebt toegevoegd of aangepast en link de issue. (PRs kunnen alleen gemaakt worden door @amsterdam.nl accounts)

### 8. Branching Strategie

*   **`main`**: Production - Stabiele, gepubliceerde versie. Hier mag alleen volledig werkende code staan.
*   **`development`**: Development - Speeltuin voor ontwikkelaars. Code hier kan (tijdelijk) kapot zijn. Dit is de basis voor nieuwe features.
*   **Feature Branches**: Alle taak- of feature-branches worden vernoemd naar het user story nummer en een korte beschrijving van de taak (bijv. `73822_korte_taak_beschrijving`). Deze worden aangemaakt *vanuit* de `development` branch en gemerged *terug naar* `development` via een Pull Request.

