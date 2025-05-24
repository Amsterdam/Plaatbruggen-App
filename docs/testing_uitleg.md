# Testing Uitleg: Automatische Tests voor Brugtoetsingsproject

Dit document legt uit hoe ons automatische testsysteem werkt, hoe je ermee werkt, en hoe je problemen oplost.

## 🎯 Wat Deze Tests Doen

Ons project heeft **~200 automatische tests** die controleren:
1. **Kernberekeningen werken**: Brugberekeningen, belastingen, en toetsen
2. **VIKTOR interface functioneert**: Views, controllers, en parametrization
3. **Geen regressies**: Vangt kapotte functionaliteit op voordat het productie bereikt

## 🔄 Push Workflow

### ✅ Succes Scenario
```bash
git push origin feature-branch
```
**Resultaat:**
```
✅ Code style check passed!
✅ Type checking passed! 
✅ Tests completed successfully! 188/188 tests passed.
```
→ Push slaagt, je kunt een Pull Request maken.

### ❌ Faal Scenario
```bash
git push origin feature-branch
```
**Resultaat:**
```
❌ Tests failed! 3 failures out of 188 tests.

🔥 CONTROLLER TEST FAILURE! 🔥
Test: test_calculate_bridge_loads
Error: AssertionError: Expected load factor 1.35, got 1.0
```
→ Push wordt geweigerd. Los eerst de fouten op.

## 🧪 Test Types

### Core Logic Tests (`tests/test_src/`) - 120 tests
Testen berekeningen onafhankelijk van VIKTOR:

```python
def test_permanent_load_factor(self):
    """Test permanente belasting factor berekening."""
    factor = calculate_permanent_load_factor("unfavorable")
    self.assertEqual(factor, 1.35)  # Eurocode standaard
```

### VIKTOR Interface Tests (`tests/test_app/`) - 68 tests
Testen de VIKTOR interface:

```python
def test_get_3d_view_execution(self):
    """Test 3D view generatie."""
    result = self.controller.get_3d_view(self.default_params)
    self.assertIsInstance(result, GeometryResult)
```

## 🛠️ Wanneer Tests Toevoegen/Wijzigen

### Nieuwe Functionaliteit Toevoegen
1. **Schrijf eerst de test:**
```python
def test_new_calculation_method(self):
    result = new_calculation_method(input_data)
    self.assertEqual(result.factor, expected_value)
```

2. **Implementeer functie:**
```python
def new_calculation_method(input_data):
    return CalculationResult(factor=calculated_value)
```

### Bestaande Code Wijzigen
Update tests wanneer je verwacht gedrag verandert:
```python
# Voor: string output
def test_old_behavior(self):
    result = some_function()
    self.assertEqual(result, "old_format")

# Na: dictionary output  
def test_new_behavior(self):
    result = some_function()
    self.assertEqual(result, {"value": "new_format", "status": "ok"})
```

## 📁 Test Structuur

```
tests/
├── test_app/           # VIKTOR interface tests (68)
│   ├── test_bridge/
│   │   ├── test_controller.py
│   │   └── test_controller_views.py
│   └── test_overview_bridges/
└── test_src/           # Core logic tests (120)
    ├── test_bridge_analysis/
    └── test_common/
```

## 🚀 Tests Draaien

```bash
# Alle tests
python run_enhanced_tests.py

# Specifieke test
python -m unittest tests.test_src.test_common.test_gis_utils.TestGISUtils.test_specific_function -v

# Specifieke module
python -m unittest tests.test_app.test_bridge.test_controller_views -v
```

## 📄 Seed Files

Gebruik seed files voor complexe testdata:

```python
# tests/test_data/bridge_default_params.json
{
    "info": {"bridge_name": "Test Brug"},
    "geometry": {"length": 30.0, "width": 12.0}
}

# In tests:
def setUp(self):
    self.default_params = load_bridge_default_params()
```

**⚠️ Belangrijk:** Update seed files wanneer je parametrization wijzigt!

```python
# Parameter toegevoegd in parametrization.py:
input.geometry.height = NumberField("Hoogte", default=5.0)

# Update seed file:
{
    "geometry": {
        "length": 30.0,
        "width": 12.0,
        "height": 5.0  // ← VOEG DIT TOE
    }
}
```

## 🐛 Falende Tests Debuggen

1. **Lees de foutmelding:**
```
Test: test_calculate_bridge_loads
Error: AssertionError: Expected load factor 1.35, got 1.0
```

2. **Draai lokaal:**
```bash
python -m unittest tests.test_app.test_bridge.test_controller.TestBridgeController.test_calculate_bridge_loads -v
```

3. **Los het probleem op:**
   - Check of je wijzigingen de verwachte output beïnvloedden
   - Verifieer of test verwachtingen nog kloppen
   - Update test als nieuwe functionaliteit correct is

## 🤖 AI Hulp Krijgen

Wanneer je vastzit, vraag een AI model om hulp met deze template:

```
Ik heb een falende test in mijn Python/VIKTOR project:

**Fout:** AssertionError: Expected load factor 1.35, got 1.0

**Test Code:**
[plak test code]

**Functie die getest wordt:**
[plak functie code]

**Wat ik veranderde:**
[beschrijf je wijzigingen]

**Vraag:** Is mijn test correct, of moet ik de functie repareren?
```

AI kan helpen met:
- Test logica uitleg
- Verwachtingen controleren tegen standaarden
- Mock setup voor VIKTOR tests
- Seed file structuur
- Edge case identificatie

## ✅ Best Practices

**WEL DOEN:**
- Schrijf tests voor nieuwe functies voordat je implementeert
- Gebruik beschrijvende testnamen: `test_bridge_load_calculation_with_traffic_load`
- Test edge cases: lege input, None waarden, extreme getallen
- Update tests bij functionaliteit wijzigingen
- Update seed files bij parameter wijzigingen
- Vraag AI om hulp wanneer je vastzit

**NIET DOEN:**
- Tests overslaan om push te laten slagen
- Tests verwijderen zonder goede reden
- Complexe logica in tests gebruiken
- Echte files/databases gebruiken in tests
- Seed files vergeten bij parametrization wijzigingen

## 🆘 Hulp Nodig?

- **Test faalt, weet niet waarom?** → Draai lokaal, check fout, of vraag AI
- **Nieuwe functie, welke test?** → Kijk naar vergelijkbare tests in zelfde module
- **VIKTOR test problemen?** → Check `tests/test_app/test_bridge/test_controller_views.py`
- **Core logic test problemen?** → Check `tests/test_src/` voorbeelden
- **Seed file updates?** → Check alle JSON files in `tests/test_data/`