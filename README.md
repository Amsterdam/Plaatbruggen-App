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

### 5. Werk op een eigen branch
De branch word aangemaakt via de issues. Bij het forken van de code fork je ook de aangemaakte branch bij je eerstvolgende pull.
```bash
git checkout feature/naam-van-je-feature
# voer je wijzigingen door
git commit -m "Duidelijke commit message"
git push origin feature/naam-van-je-feature
```

### 6. Maak een Pull Request aan
Ga naar je fork op GitHub en klik op **"Compare & pull request"**  
Kies `Amsterdam/automatisch-toetsmodel-plaatbruggen:main` als doelbranch.  
Beschrijf duidelijk wat je hebt toegevoegd of aangepast.

