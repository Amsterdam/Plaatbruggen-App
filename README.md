# Plaatbruggen-App## 🔄 Workflow voor samenwerking (Fork & Pull Request)

Omdat de repository openbaar is en sommige teamleden (nog) geen toegang hebben tot de organisatie, gebruiken we een **fork-based workflow**. Volg de stappen hieronder om samen te werken aan deze repository.

### 1. Fork de repository
Ga naar [https://github.com/Amsterdam/Plaatbruggen-App](https://github.com/Amsterdam/Plaatbruggen-App)  
Klik rechtsboven op **"Fork"** en kies je eigen GitHub-account.

### 2. Clone je fork lokaal
```bash
git clone https://github.com/<jouw-gebruikersnaam>/Plaatbruggen-App.git
cd Plaatbruggen-App
```

### 3. Voeg de originele repo toe als upstream
```bash
git remote add upstream https://github.com/Amsterdam/Plaatbruggen-App.git
```

### 4. Blijf up-to-date met de hoofdrepo
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 5. Werk op een eigen branch
```bash
git checkout -b feature/naam-van-je-feature
# voer je wijzigingen door
git commit -m "Duidelijke commit message"
git push origin feature/naam-van-je-feature
```

### 6. Maak een Pull Request aan
Ga naar je fork op GitHub en klik op **"Compare & pull request"**  
Kies `Amsterdam/Plaatbruggen-App:main` als doelbranch.  
Beschrijf duidelijk wat je hebt toegevoegd of aangepast.

