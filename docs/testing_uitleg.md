# Testing Uitleg: Automatische Tests voor het Brugtoetsingsproject

Dit document legt uit hoe ons automatische testsysteem werkt, waarom we het hebben, en hoe je ermee omgaat als ontwikkelaar.

## 🎯 Wat Doen Deze Tests?

Ons project heeft **ongeveer 200 automatische tests** die controleren of de code correct werkt. Deze tests draaien automatisch wanneer je code pusht naar GitHub en zorgen ervoor dat:

1. **Kernberekeningen kloppen**: Tests controleren of brugberekeningen, belastingen, en toetsen correct uitgevoerd worden
2. **VIKTOR interface werkt**: Tests controleren of alle views, controllers en parametrization correct functioneren  
3. **Geen regressies**: Als iemand per ongeluk iets kapot maakt, vangen de tests dit op

## 🔄 Praktische Workflow: Wat Gebeurt Er Als Je Pusht?

### Scenario 1: Alles Gaat Goed ✅
```bash
# Collega A maakt een wijziging en pusht
git add .
git commit -m "Fix bridge geometry calculation"
git push origin feature-branch
```

**Resultaat:**
```
✅ Code style check passed!
✅ Type checking passed! 
✅ Tests completed successfully! 188/188 tests passed.
```
→ **Push slaagt**, je kunt een Pull Request maken.

### Scenario 2: Test Faalt ❌
```bash
# Collega B maakt een wijziging die iets kapot maakt
git push origin another-feature
```

**Resultaat:**
```
❌ Code style check failed, please fix before pushing!
❌ Type checking failed, please fix before pushing!  
❌ Tests failed! 3 failures out of 188 tests.

🔥 CONTROLLER TEST FAILURE! 🔥
Test: test_calculate_bridge_loads
Controller: BridgeController
Function: test_calculate_bridge_loads

💥 Error Details:
AssertionError: Expected load factor 1.35, got 1.0
```
→ **Push wordt geweigerd**. Collega B moet eerst de fouten oplossen.

## 🧪 Soorten Tests in Ons Project

### 1. **Core Logic Tests** (`tests/test_src/`) - 120 tests
Deze testen de kernberekeningen onafhankelijk van VIKTOR:

```python
# Voorbeeld: test_load_factors.py
def test_permanent_load_factor(self):
    """Test of permanente belasting factor correct wordt berekend."""
    factor = calculate_permanent_load_factor("unfavorable")
    self.assertEqual(factor, 1.35)  # Verwacht 1.35 volgens Eurocode
```

**Wanneer voeg je deze toe?**
- Als je nieuwe berekeningsfuncties toevoegt in `src/`
- Als je bestaande berekeningen wijzigt
- Bij bugfixes in de kernlogica

### 2. **VIKTOR Interface Tests** (`tests/test_app/`) - 68 tests  
Deze testen of de VIKTOR interface correct werkt:

```python
# Voorbeeld: test_controller_views.py
def test_get_3d_view_execution(self):
    """Test of 3D view correct wordt gegenereerd."""
    result = self.controller.get_3d_view(self.default_params)
    self.assertIsInstance(result, GeometryResult)
    # Controleert of een 3D model wordt geretourneerd
```

**Wanneer voeg je deze toe?**
- Als je nieuwe views toevoegt aan controllers
- Als je parametrization wijzigt
- Bij wijzigingen aan de VIKTOR interface

## 🛠️ Wanneer En Hoe Tests Toevoegen/Wijzigen?

### Nieuwe Functie Toevoegen

**Stap 1: Schrijf eerst de test** (Test-Driven Development)
```python
# tests/test_src/test_bridge_analysis/test_new_feature.py
def test_new_calculation_method(self):
    """Test de nieuwe berekeningsmethod."""
    result = new_calculation_method(input_data)
    self.assertEqual(result.factor, expected_value)
```

**Stap 2: Implementeer de functie**
```python
# src/bridge_analysis/calculators/new_calculator.py
def new_calculation_method(input_data):
    # Implementatie hier
    return CalculationResult(factor=calculated_value)
```

**Stap 3: Test draait groen** ✅

### Bestaande Functie Wijzigen

Als je een bestaande functie wijzigt, moet je vaak ook de tests aanpassen:

```python
# Voor: verwachte output was string
def test_old_behavior(self):
    result = some_function()
    self.assertEqual(result, "old_format")

# Na: nieuwe output is dictionary  
def test_new_behavior(self):
    result = some_function()
    self.assertEqual(result, {"value": "new_format", "status": "ok"})
```

## 🎨 Test File Structuur

Tests volgen de mapstructuur van de hoofdcode:

```
automatisch-toetsmodel-plaatbruggen/
├── app/
│   ├── bridge/
│   │   └── controller.py
│   └── overview_bridges/
│       └── controller.py
├── src/
│   ├── bridge_analysis/
│   │   └── calculators/
│   └── common/
│       └── gis_utils.py
└── tests/
    ├── test_app/           # 68 tests
    │   ├── test_bridge/
    │   │   ├── test_controller.py
    │   │   └── test_controller_views.py
    │   └── test_overview_bridges/
    │       └── test_controller_views.py
    └── test_src/           # 120 tests
        ├── test_bridge_analysis/
        └── test_common/
            └── test_gis_utils.py
```

## 🚀 Tests Lokaal Draaien

### Alle Tests
```bash
python run_enhanced_tests.py
```

### Specifieke Test
```bash
python -m unittest tests.test_src.test_common.test_gis_utils.TestGISUtils.test_specific_function -v
```

### Tests voor Specifieke Module
```bash
python -m unittest tests.test_app.test_bridge.test_controller_views -v
```

## 🔧 Test Data en Seed Files

Voor complexe tests gebruiken we **seed files** met voorbeelddata:

```python
# tests/test_data/bridge_default_params.json
{
    "info": {
        "bridge_name": "Test Brug",
        "bridge_id": "12345"
    },
    "geometry": {
        "length": 30.0,
        "width": 12.0
    }
}

# In test gebruik:
def setUp(self):
    self.default_params = load_bridge_default_params()
    
def test_with_realistic_data(self):
    result = self.controller.some_method(self.default_params)
    # Test met realistische brugdata
```

### 🔄 Seed Files Onderhouden bij Parameter Wijzigingen

**Belangrijk:** Wanneer je parameters toevoegt, hernoemt, of verwijdert in `parametrization.py`, **moet je ook de seed files updaten**!

#### Scenario: Nieuwe Parameter Toegevoegd
```python
# In app/bridge/parametrization.py
input.geometry.new_height_field = NumberField("Hoogte", default=5.0)
```

**Update de seed files:**
```json
// tests/test_data/bridge_default_params.json
{
    "info": {
        "bridge_name": "Test Brug"
    },
    "geometry": {
        "length": 30.0,
        "width": 12.0,
        "new_height_field": 5.0  // ← TOEVOEGEN
    }
}
```

#### Scenario: Parameter Hernoemd
```python
# Oud: input.geometry.width
# Nieuw: input.geometry.bridge_width
```

**Update alle seed files:**
```json
{
    "geometry": {
        "length": 30.0,
        "bridge_width": 12.0  // ← was "width"
    }
}
```

#### Waarom Is Dit Belangrijk?
- **Tests falen** als seed data niet overeenkomt met parametrization
- **Nieuwe functionaliteit wordt niet getest** als parameters ontbreken in seed files
- **Foutieve testresultaten** als oude parameter namen gebruikt worden

## 🐛 Test Failures Debuggen

### Stap 1: Lees de Error Boodschap
```
🔥 CONTROLLER TEST FAILURE! 🔥
Test: test_calculate_bridge_loads
Error: AssertionError: Expected load factor 1.35, got 1.0
```

### Stap 2: Lokaal Reproduceren
```bash
python -m unittest tests.test_app.test_bridge.test_controller.TestBridgeController.test_calculate_bridge_loads -v
```

### Stap 3: Debug de Code
- Check of je wijzigingen de verwachte output hebben veranderd
- Controleer of de test nog klopt met de nieuwe implementatie
- Update de test als de nieuwe functionaliteit correct is

## 🤖 AI Hulp bij Test Fixes

Vastzittend met een falende test? Je kunt een AI model (zoals ChatGPT, Claude, of Cursor) vragen om te helpen!

### Voorbeeld Prompt voor AI Hulp:

```
Ik heb een falende test in mijn Python/VIKTOR project. Kun je helpen?

**Fout:**
AssertionError: Expected load factor 1.35, got 1.0

**Test Code:**
```python
def test_calculate_bridge_loads(self):
    result = calculate_permanent_load_factor("unfavorable")
    self.assertEqual(result, 1.35)
```

**Functie die getest wordt:**
```python
def calculate_permanent_load_factor(condition):
    if condition == "unfavorable":
        return 1.35
    return 1.0
```

**Wat ik heb gewijzigd:**
Ik heb de default waarde in de functie aangepast van 1.35 naar 1.0.

**Vraag:** 
Is mijn test nog correct, of moet ik de functie aanpassen? Wat verwacht Eurocode voor permanente belastingen?
```

### Tips voor Goede AI Prompts:
- **Geef de exacte foutmelding** inclusief traceback
- **Deel de relevante code** (test + functie die getest wordt)
- **Leg uit wat je hebt gewijzigd** voor de test faalde
- **Vraag specifieke hulp** (test aanpassen vs. code aanpassen)
- **Geef context** (Eurocode, VIKTOR SDK, etc.)

### Wat AI Kan Helpen Met:
✅ **Test logic uitleggen** en fouten identificeren  
✅ **Verwachtingen controleren** tegen normen/standaarden  
✅ **Mockup setup** voor complexe VIKTOR tests  
✅ **Seed file structuur** aanpassen  
✅ **Edge cases** identificeren die getest moeten worden  

## 🎯 Best Practices

### DO ✅
- **Schrijf tests voor nieuwe functies** voordat je ze implementeert
- **Gebruik beschrijvende testnamen**: `test_bridge_load_calculation_with_traffic_load`
- **Test edge cases**: lege input, None waarden, extreme getallen
- **Update tests** wanneer je functionaliteit wijzigt
- **Update seed files** bij parameter wijzigingen
- **Vraag AI om hulp** als je vastloopt

### DON'T ❌
- **Geen tests skippen** om push te laten slagen
- **Geen tests verwijderen** zonder goede reden
- **Geen complexe logic in tests** - tests moeten simpel en begrijpelijk zijn
- **Geen echte files/databases** gebruiken in tests - gebruik mocks
- **Seed files niet vergeten** bij parametrization changes

## 📞 Hulp Nodig?

- **Test faalt en je weet niet waarom?** → Draai lokaal en check de error message, of vraag AI om hulp
- **Nieuwe functie, welke test schrijven?** → Kijk naar vergelijkbare tests in dezelfde module
- **VIKTOR test problemen?** → Check `tests/test_app/test_bridge/test_controller_views.py` voor voorbeelden
- **Core logic test problemen?** → Check `tests/test_src/` voor eenvoudige unit test voorbeelden
- **Seed files updaten?** → Check alle JSON files in `tests/test_data/` na parameter wijzigingen
- **AI prompt nodig?** → Gebruik het voorbeeld template hierboven

Met dit testsysteem kunnen we met vertrouwen wijzigingen maken, wetende dat bestaande functionaliteit beschermd is! 🛡️ 