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

System posiada kompleksowy zestaw **84 testów automatycznych** (68 jednostkowych + 16 integracyjnych) ustandaryzowanych według konwencji **AAA (Arrange-Act-Assert)** z jedną logiczną asercją na test.

### 1. Testy jednostkowe (`test/unit/`)
Wszystkie testy jednostkowe badają logikę biznesową w pełnej izolacji, bez udziału operacji wejścia/wyjścia czy bazy danych:

* **[test/unit/test_money.py](test/unit/test_money.py) (23 testy):**
  * Weryfikacja niezmienności obiektu wartości `Money` i precyzyjnego zaokrąglenia `ROUND_HALF_UP` do 2 miejsc po przecinku.
  * Blokada użycia typu zmiennoprzecinkowego `float` (`TypeError`).
  * Pełna arytmetyka: dodawanie, odejmowanie, mnożenie przez skalar (`Decimal`/`int`) oraz mnożenie lewostronne (`rmul`).
  * Pełen zestaw operatorów porównania: `<`, `<=`, `>`, `>=` z obsługą walidacji typu (`NotImplemented`).
  * Walidacja niezgodności walut przy próbie sumowania lub porównywania (`ValueError`).
  * Formatowanie czytelnego łańcucha znaków (`123.45 PLN`).

* **[test/unit/test_plan.py](test/unit/test_plan.py) (4 testy):**
  * Poprawne tworzenie planu subskrypcyjnego z parametrami bazowymi.
  * Walidacja typu poziomu planu (`PlanTier`).
  * Walidacja typu ceny bazowej (wymóg instancji `Money`).
  * Zabezpieczenie przed ujemną liczbą zapytań w cenie (`ValueError`).

* **[test/unit/test_subscription.py](test/unit/test_subscription.py) (13 testów):**
  * Domyślna inicjalizacja subskrypcji w stanie początkowym `TRIAL`.
  * Dozwolone przejścia stanów cyklu życia: `TRIAL` &rarr; `ACTIVE` &rarr; `PAST_DUE` &rarr; `ACTIVE` oraz anulowanie do `CANCELLED`.
  * Idempotentność powtórnej aktywacji i anulowania.
  * Zabezpieczenie przed reaktywacją anulowanej subskrypcji (`InvalidStateTransitionError`).
  * Zabezpieczenie przed oznaczeniem zaległości (`mark_past_due`) z innych stanów niż `ACTIVE`.
  * Rejestrowanie zapytań API oraz blokada wartości ujemnych (`ValueError`).
  * Zmiana przypisanego planu z walidacją instancji (`change_plan`).

* **[test/unit/test_pricing_strategy.py](test/unit/test_pricing_strategy.py) (6 testów):**
  * Obliczanie stałego abonamentu ryczałtowego (`FlatRatePricingStrategy`) niezależnie od liczby zapytań.
  * Zerowa dopłata w cenniku progowym (`TieredUsagePricingStrategy`), gdy zużycie mieści się w limicie wliczonym w plan.
  * Naliczanie dopłaty progowej w pierwszym przedziale (do 5000 req po 0.05 PLN).
  * Naliczanie dopłaty progowej w drugim przedziale (powyżej 5000 req po 0.02 PLN).
  * Rzucanie `ValueError` przy ujemnych jednostkach zużycia dla obu strategii.

* **[test/unit/test_proration_engine.py](test/unit/test_proration_engine.py) (9 testów):**
  * Obliczanie 100% kredytu w dniu 0 oraz 50% kredytu w 15. dniu 30-dniowego cyklu.
  * Obliczanie zerowego kredytu w ostatnim (30.) dniu cyklu.
  * Kalkulacja dopłaty netto przy przejściu na wyższą taryfę (*upgrade*).
  * Kalkulacja salda kredytowego przy przejściu na niższą taryfę (*downgrade*).
  * Blokada migracji pomiędzy różnymi walutami rozliczeniowymi (`ValueError`).
  * Walidacja przekroczenia długości cyklu oraz ujemnych wartości dni.

* **[test/unit/test_billing_service.py](test/unit/test_billing_service.py) (8 testów):**
  * Tworzenie i zapisywanie aktywnej subskrypcji w repozytorium.
  * Wyliczanie miesięcznej faktury z uwzględnieniem zarejestrowanego zużycia i strategii cenowej.
  * Orkiestracja migracji planu (obliczenie kwot, aktualizacja stanu encji i repozytorium).
  * Anulowanie subskrypcji i utrwalenie zmiany statusu.
  * Obsługa wyjątków `KeyError` przy operacjach na nieistniejących identyfikatorach.
  * Pobieranie listy wszystkich zarejestrowanych subskrypcji.

* **[test/unit/test_repository.py](test/unit/test_repository.py) (5 testów):**
  * Zapis i pobieranie subskrypcji po ID z pamięci podręcznej.
  * Zwracanie `None` przy braku rekordu.
  * Pobieranie listy wszystkich subskrypcji.
  * Usuwanie subskrypcji po identyfikatorze.
  * Czyszczenie całego magazynu danych (`clear()`).

---

### 2. Testy integracyjne (`test/integration/`)
Testy integracyjne weryfikują współpracę warstwy prezentacji, routingu Flask, walidacji wejścia oraz logiki domenowej:

* **[test/integration/test_web_routes.py](test/integration/test_web_routes.py) (16 testów):**
  * `test_should_render_dashboard_with_200_ok`: Poprawne renderowanie głównego panelu nawigacyjnego.
  * `test_should_return_plans_catalog_via_json_api`: Pobranie katalogu taryf przez REST API (`200 OK`).
  * `test_should_calculate_proration_via_rest_api`: Dynamiczne wyliczenie rozliczenia proration przez endpoint `/api/proration/calculate`.
  * `test_should_return_400_when_proration_api_receives_invalid_payload`: Odrzucenie nieprawidłowego payloadu JSON w kalkulatorze.
  * `test_should_return_422_when_proration_api_receives_out_of_bound_day`: Obsługa błędu zakresu, gdy dzień przekracza cykl.
  * `test_should_create_new_subscription_via_form_post`: Rejestracja nowej subskrypcji formularzem HTML z przekierowaniem.
  * `test_should_return_400_when_creating_subscription_with_missing_fields`: Walidacja brakujących pól formularza.
  * `test_should_return_400_when_creating_subscription_with_invalid_tier`: Walidacja nieprawidłowego identyfikatora taryfy.
  * `test_should_migrate_subscription_and_redirect_to_dashboard`: Zmiana planu subskrypcji formularzem HTML.
  * `test_should_return_404_when_migrating_non_existent_subscription`: Zwrócenie kodu 404 przy migracji nieznanej subskrypcji.
  * `test_should_return_400_when_migrating_with_invalid_day_format`: Zwrócenie kodu 400 przy nieliczbowym dniu cyklu.
  * `test_should_return_422_when_migrating_with_day_exceeding_cycle`: Zwrócenie kodu 422 przy dniu poza zakresem cyklu.
  * `test_should_cancel_subscription_via_form_post`: Poprawne anulowanie subskrypcji przez żądanie POST.
  * `test_should_return_404_when_cancelling_non_existent_subscription`: Obsługa błędu 404 przy anulowaniu nieistniejącego rekordu.
  * `test_should_render_invoice_page_with_200_ok`: Wyświetlenie wizualnej faktury dla aktywnej subskrypcji.
  * `test_should_return_404_when_viewing_invoice_for_non_existent_subscription`: Zwrócenie kodu 404 przy próbie podglądu faktury nieistniejącej subskrypcji.

---

### 3. Uruchomienie testów i raport pokrycia

#### Uruchomienie pełnego pakietu testów:
```bash
python -m unittest discover -s test -p "test_*.py" -v
```

#### Badanie pokrycia kodu (Coverage):
```bash
python -m coverage run -m unittest discover -s test -p "test_*.py"
python -m coverage report -m
```

#### Raport pokrycia kodu (Wynik: 99%):
```text
Name                               Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------------
src\config.py                          9      0      0      0   100%
src\models\currency.py                 5      0      0      0   100%
src\models\money.py                   61      0     24      0   100%
src\models\plan.py                    22      0      6      0   100%
src\models\subscription.py            38      0     10      0   100%
src\repositories\base.py               7      0      0      0   100%
src\repositories\in_memory.py         15      0      0      0   100%
src\services\billing_service.py       41      0      6      0   100%
src\services\pricing_strategy.py      31      1      6      0    97%   20
src\services\proration_engine.py      43      0     10      0   100%
------------------------------------------------------------------------------
TOTAL                                272      1     62      0    99%
```


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
