# SaaSBillingEngine

![Python](https://img.shields.io/badge/Language-Python_3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Flask_3.1-000000?style=flat-square&logo=flask&logoColor=white)
![Styling](https://img.shields.io/badge/Styling-Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Testing](https://img.shields.io/badge/Testing-unittest_%26_coverage-FFD43B?style=flat-square&logo=python&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-SOLID_%26_Clean_Code-4B5563?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## Nazwa kursu
**Testowanie i Jakość Oprogramowania II**  
Wydział Politechniczny, Katedra Informatyki  
Akademia Tarnowska  
Prowadzący: **dr inż. Tomasz Gądek**

---

## Autor
* **Student:** Kacper Szczudło
* **Nr indeksu:** 37738
* **Grupa:** PT2

---

## Temat projektu
**SaaSBillingEngine — System rozliczeń subskrypcyjnych i fakturowania SaaS**

---

## Opis projektu
**SaaSBillingEngine** to modułowy silnik rozliczeń abonamentowych dla platform typu Software-as-a-Service (SaaS), zaprojektowany zgodnie z paradygmatami **Domain-Driven Design (DDD)**, zasadami **SOLID** oraz standardami czystego kodu.

Główne odpowiedzialności systemu:
1. **Proration Engine (Rozliczenia proporcjonalne):** Precyzyjne wyliczanie wartości niewykorzystanego abonamentu, kosztu nowego planu za pozostałe dni oraz kwoty dopłaty netto lub salda kredytowego przy migracji planu (upgrade/downgrade) w trakcie 30-dniowego cyklu rozliczeniowego.
2. **Precyzyjna arytmetyka finansowa (`Money` Value Object):** Całkowita eliminacja błędów zmiennoprzecinkowych typu `float` na rzecz obiektów niezmiennych operujących na typie `Decimal` z zaokrągleniem bankowym (`ROUND_HALF_UP`).
3. **Wzorzec Strategy w taryfikacji:** Elastyczne modele naliczania opłat:
   * `FlatRatePricingStrategy` — stała opłata abonamentowa (ryczałt),
   * `TieredUsagePricingStrategy` — model progowy z automatycznymi dopłatami za nadmiarowe zapytania API ponad limit w planie.
4. **Wzorzec State w cyklu życia subskrypcji:** Enkapsulacja dozwolonych przejść stanów w modelu (`TRIAL` &rarr; `ACTIVE` &rarr; `PAST_DUE` &rarr; `CANCELLED`) z blokadą niepoprawnych operacji.
5. **Wzorzec Repository (DIP):** Całkowita izolacja warstwy biznesowej od magazynu danych dzięki protokołowi `SubscriptionRepository` i implementacji `InMemorySubscriptionRepository`.
6. **Interfejs graficzny Product UI:** Panel webowy zbudowany we Flasku i Tailwind CSS (konsola *Proration Workbench* na żywo, katalog taryf, rejestr subskrypcji oraz gotowy do druku widok faktury rozliczeniowej B2B).

---

## Uruchomienie projektu

### Wymagania wstępne
* Python w wersji `3.10` lub nowszej (rekomendowany `3.12`)
* Menedżer pakietów `pip`

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/kacperszczudlo/SaaSBillingEngine.git
cd SaaSBillingEngine
```

### 2. Utworzenie i aktywacja środowiska wirtualnego
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 4. Uruchomienie serwera aplikacji
```bash
python -m src.web.app
```

Aplikacja dostępna jest w przeglądarce pod adresem:  
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Testy

System posiada kompleksowy zestaw testów automatycznych zorganizowany z podziałem na warstwy:
* **Testy jednostkowe (`test/unit/`):** Testy domeny finansowej `Money`, wzorców `PricingStrategy`, silnika `ProrationEngine`, maszyny stanów `Subscription` oraz repozytorium `InMemory`.
* **Testy integracyjne (`test/integration/`):** Testy tras i kontrolerów Flask (`test_client`) weryfikujące obsługę żądań HTTP, kody statusu (200, 400, 404, 422) oraz endpointy REST API.

### Uruchomienie wszystkich testów
```bash
python -m unittest discover -s test -p "test_*.py" -v
```

### Badanie pokrycia kodu (Coverage)
```bash
python -m coverage run -m unittest discover -s test -p "test_*.py"
python -m coverage report -m
```

> **Uwaga:** Szczegółowy wykaz testów jednostkowych i integracyjnych z odnośnikami do plików źródłowych stanowi przedmiot **Etapu 2** harmonogramu projektu.

---

## Dokumentacja API

Aplikacja udostępnia interfejs REST API wykorzystywany przez interfejs oraz klientów zewnętrznych:

| Metoda HTTP | Endpoint | Opis |
| :--- | :--- | :--- |
| `GET` | `/` | Główny pulpit nawigacyjny (Dashboard UI) |
| `GET` | `/api/plans` | Pobranie pełnego katalogu planów subskrypcyjnych w formacie JSON |
| `POST` | `/api/proration/calculate` | Obliczenie proporcjonalnej zmiany taryfy (REST API dla symulatora) |
| `POST` | `/subscriptions` | Utworzenie i aktywacja nowej subskrypcji |
| `POST` | `/subscriptions/<id>/migrate` | Przeprowadzenie migracji planu subskrypcji |
| `POST` | `/subscriptions/<id>/cancel` | Anulowanie subskrypcji |
| `GET` | `/subscriptions/<id>/invoice` | Wygenerowanie widoku faktury rozliczeniowej |

> **Uwaga:** Pełna specyfikacja kontraktów żądań i odpowiedzi JSON zostanie rozszerzona w ramach **Etapu 3**.

---

## Przypadki testowe dla testera manualnego (TestCase)
Szczegółowa macierz 10 formalnych scenariuszy testowych (ID, Warunki początkowe, Kroki testowe, Oczekiwany rezultat) zostanie dołączona w dokumentacji końcowej w ramach **Etapu 3** harmonogramu.

---

## Technologie użyte w projekcie
* **Język programowania:** Python 3.12
* **Framework webowy:** Flask 3.1
* **Styling & UI:** Tailwind CSS (CDN), Inter Font, JetBrains Mono
* **Arytmetyka finansowa:** `decimal.Decimal` (precyzja walutowa, brak błędów `float`)
* **Testowanie:** `unittest` (konwencja AAA), `unittest.mock`
* **Analiza jakości:** `coverage.py` (badanie branch coverage)
* **Kontrola wersji:** Git / GitHub
