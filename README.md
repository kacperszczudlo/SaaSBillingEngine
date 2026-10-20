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
**SaaSBillingEngine: System rozliczeń subskrypcyjnych i fakturowania SaaS**

---

## Opis projektu
**SaaSBillingEngine** to silnik rozliczeń abonamentowych dla platform Software-as-a-Service (SaaS), zaprojektowany zgodnie z paradygmatami **Domain-Driven Design (DDD)**, zasadami **SOLID** oraz standardami czystego kodu.

Główne odpowiedzialności systemu:
1. **Proration Engine (Rozliczenia proporcjonalne):** Precyzyjne wyliczanie wartości niewykorzystanego abonamentu, kosztu nowego planu za pozostałe dni oraz kwoty dopłaty netto lub salda kredytowego przy migracji planu (upgrade/downgrade) w trakcie 30-dniowego cyklu rozliczeniowego.
2. **Precyzyjna arytmetyka finansowa (`Money` Value Object):** Całkowita eliminacja błędów zmiennoprzecinkowych typu `float` na rzecz obiektów niezmiennych operujących na typie `Decimal` z zaokrągleniem bankowym (`ROUND_HALF_UP`).
3. **Wzorzec Strategy w taryfikacji:** Modele naliczania opłat:
   * `FlatRatePricingStrategy`: stała opłata abonamentowa (ryczałt),
   * `TieredUsagePricingStrategy`: model progowy z dopłatami za nadmiarowe zapytania API ponad limit w planie.
4. **Wzorzec State w cyklu życia subskrypcji:** Enkapsulacja dozwolonych przejść stanów w modelu (`TRIAL` -> `ACTIVE` -> `PAST_DUE` -> `CANCELLED`) z blokadą niepoprawnych operacji.
5. **Wzorzec Repository (DIP):** Całkowita izolacja warstwy biznesowej od magazynu danych dzięki protokołowi `SubscriptionRepository` i implementacji `InMemorySubscriptionRepository`.
6. **Interfejs graficzny Product UI:** Panel webowy zbudowany we Flasku i Tailwind CSS (kalkulator rozliczeń proporcjonalnych na żywo, katalog taryf, rejestr subskrypcji oraz gotowy do druku widok faktury rozliczeniowej B2B).

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

Pakiet testowy obejmuje **84 testy automatyczne** (68 jednostkowych oraz 16 integracyjnych) przygotowane w konwencji **AAA (Arrange-Act-Assert)** z jedną logiczną asercją na test.

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
  * Dozwolone przejścia stanów cyklu życia: `TRIAL` -> `ACTIVE` -> `PAST_DUE` -> `ACTIVE` oraz anulowanie do `CANCELLED`.
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

Aplikacja udostępnia interfejs programistyczny HTTP (REST API) oraz punkty końcowe obsługujące interfejs graficzny Dashboard. Komunikacja maszynowa wykorzystuje format JSON oraz standardowe kody odpowiedzi HTTP (RFC 9110).

### Zestawienie punktów końcowych

| Metoda HTTP | Endpoint | Format wejścia | Format wyjścia | Opis |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Brak | `text/html` | Główny pulpit nawigacyjny (Dashboard UI) |
| `GET` | `/api/plans` | Brak | `application/json` | Pobranie pełnego katalogu planów subskrypcyjnych |
| `POST` | `/api/proration/calculate` | `application/json` | `application/json` | Dynamiczne obliczenie proporcjonalnej zmiany taryfy |
| `POST` | `/subscriptions` | Form data | HTML / Redirect (`302`) | Utworzenie i aktywacja nowej subskrypcji |
| `POST` | `/subscriptions/<id>/migrate` | Form data | HTML / Redirect (`302`) | Przeprowadzenie migracji planu subskrypcji |
| `POST` | `/subscriptions/<id>/cancel` | Form data | HTML / Redirect (`302`) | Anulowanie subskrypcji |
| `GET` | `/subscriptions/<id>/invoice` | Brak | `text/html` | Wygenerowanie widoku faktury rozliczeniowej |

---

### Szczegółowa specyfikacja kontraktów API

#### 1. Pobranie katalogu planów (`GET /api/plans`)
Zwraca listę wszystkich dostępnych taryf subskrypcyjnych z ich cenami bazowymi oraz limitami wliczonych zapytań API.

* **Nagłówki żądania:**
  ```http
  Accept: application/json
  ```
* **Odpowiedź sukcesu (`200 OK`):**
  ```json
  [
    {
      "tier": "starter",
      "name": "Starter",
      "base_price": "49.00",
      "currency": "PLN",
      "included_requests": 1000,
      "description": "Dla małych zespołów i początkujących projektów"
    },
    {
      "tier": "professional",
      "name": "Professional",
      "base_price": "149.00",
      "currency": "PLN",
      "included_requests": 5000,
      "description": "Dla rozwijających się firm z większym ruchem API"
    },
    {
      "tier": "enterprise",
      "name": "Enterprise",
      "base_price": "499.00",
      "currency": "PLN",
      "included_requests": 25000,
      "description": "Maksymalna wydajność, dedykowane wsparcie i brak limitów"
    }
  ]
  ```

---

#### 2. Kalkulacja proporcjonalnej migracji (`POST /api/proration/calculate`)
Umożliwia dynamiczne przeliczenie kwoty dopłaty lub salda kredytowego przy przejściu między planami w trakcie trwania cyklu rozliczeniowego.

* **Nagłówki żądania:**
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Przykładowy payload żądania:**
  ```json
  {
    "from_tier": "starter",
    "to_tier": "professional",
    "current_day": 15,
    "total_cycle_days": 30
  }
  ```
* **Parametry wejściowe:**
  * `from_tier` (string, wymagane): Identyfikator obecnego planu (`starter`, `professional`, `enterprise`).
  * `to_tier` (string, wymagane): Identyfikator planu docelowego.
  * `current_day` (integer, opcjonalne, domyślnie `15`): Dzień cyklu, w którym dokonywana jest zmiana (`0` - `total_cycle_days`).
  * `total_cycle_days` (integer, opcjonalne, domyślnie `30`): Łączna długość cyklu rozliczeniowego w dniach.

* **Odpowiedź sukcesu (`200 OK`):**
  ```json
  {
    "unused_credit": "24.50",
    "new_plan_charge": "74.50",
    "net_amount_due": "50.00",
    "credit_balance": "0.00",
    "remaining_days": 15,
    "total_cycle_days": 30,
    "currency": "PLN"
  }
  ```

* **Odpowiedzi błędów:**
  * **`400 Bad Request`**: Błędne parametry wejściowe (brak wymaganych pól, nieznany plan, niepoprawny format liczbowy):
    ```json
    {
      "error": "Nieprawidłowe parametry kalkulacji"
    }
    ```
  * **`422 Unprocessable Entity`**: Naruszenie reguł domenowych (np. dzień cyklu przekracza długość cyklu lub wartość ujemna):
    ```json
    {
      "error": "current_day (35) cannot exceed total_cycle_days (30)"
    }
    ```

---

#### 3. Tworzenie nowej subskrypcji (`POST /subscriptions`)
Tworzy i natychmiast aktywuje nową subskrypcję dla wskazanego klienta.

* **Nagłówki żądania:**
  ```http
  Content-Type: application/x-www-form-urlencoded
  ```
* **Ciało żądania (Form Data):**
  * `customer_id` (string, wymagane): Identyfikator klienta (np. `cust-101`).
  * `plan_tier` (string, wymagane): Poziom planu (`starter`, `professional`, `enterprise`).

* **Odpowiedź sukcesu (`302 Found`):**
  * Przekierowanie nagłówkiem `Location: /` na główny pulpit nawigacyjny.
* **Odpowiedzi błędów:**
  * **`400 Bad Request`**:
    ```json
    {
      "error": "Brakujące wymagane pola customer_id lub plan_tier"
    }
    ```
  * **`404 Not Found`**:
    ```json
    {
      "error": "Plan nie został odnaleziony w katalogu"
    }
    ```

---

#### 4. Migracja taryfy subskrypcji (`POST /subscriptions/<subscription_id>/migrate`)
Zmienia plan przypisany do istniejącej subskrypcji z rozliczeniem proporcjonalnym (proration).

* **Parametry ścieżki:**
  * `subscription_id` (string, wymagane): Unikalny identyfikator subskrypcji (np. `sub-001`).
* **Ciało żądania (Form Data):**
  * `target_tier` (string, wymagane): Poziom taryfy docelowej.
  * `current_day` (integer, opcjonalne, domyślnie `15`): Dzień cyklu w momencie zmiany.

* **Odpowiedź sukcesu (`302 Found`):**
  * Przekierowanie nagłówkiem `Location: /` na główny pulpit nawigacyjny.
* **Odpowiedzi błędów:**
  * **`400 Bad Request`**: Nieprawidłowy plan docelowy lub format liczbowy dnia.
  * **`404 Not Found`**:
    ```json
    {
      "error": "Subskrypcja sub-999 nie istnieje"
    }
    ```
  * **`422 Unprocessable Entity`**: Dzień cyklu poza dozwolonym zakresem.

---

#### 5. Anulowanie subskrypcji (`POST /subscriptions/<subscription_id>/cancel`)
Zmienia status subskrypcji na `CANCELLED` zgodnie z regułami maszyny stanów.

* **Parametry ścieżki:**
  * `subscription_id` (string, wymagane): Identyfikator anulowanej subskrypcji.
* **Odpowiedź sukcesu (`302 Found`):**
  * Przekierowanie nagłówkiem `Location: /`.
* **Odpowiedzi błędów:**
  * **`404 Not Found`**:
    ```json
    {
      "error": "Subskrypcja sub-999 nie istnieje"
    }
    ```

---

#### 6. Podgląd faktury rozliczeniowej (`GET /subscriptions/<subscription_id>/invoice`)
Generuje czytelny dokument rozliczeniowy w widoku HTML dla podanej subskrypcji.

* **Parametry ścieżki:**
  * `subscription_id` (string, wymagane): Identyfikator subskrypcji.
* **Odpowiedź sukcesu (`200 OK`):**
  * Zwraca wyrenderowany szablon HTML `invoice.html` z wyszczególnieniem opłaty bazowej, wykorzystanych zapytań i kwoty końcowej.
* **Odpowiedzi błędów:**
  * **`404 Not Found`**:
    ```json
    {
      "error": "Subskrypcja nie istnieje"
    }
    ```

---

## Przypadki testowe dla testera manualnego (TestCase)

Poniższe tabele zawierają zestaw **10 scenariuszy testowych** dla testera manualnego, przygotowanych w formacie tabelarycznym ze strony 4 instrukcji laboratoryjnej.

---

### Przypadek testowy TC001
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC001` |
| **Tytuł** | Poprawne renderowanie katalogu planów i cennika na stronie głównej |
| **Warunki początkowe** | Serwer aplikacji uruchomiony lokalnie pod adresem `http://127.0.0.1:5000`. Przeglądarka internetowa otwarta. |
| **Kroki testowe** | 1. Otwórz w przeglądarce adres `http://127.0.0.1:5000/`.<br>2. Zlokalizuj sekcję "Dostępne plany subskrypcyjne".<br>3. Zweryfikuj obecność kafelków taryf: Starter, Professional, Enterprise.<br>4. Sprawdź wyświetlane ceny oraz limity zapytań API dla każdego planu. |
| **Oczekiwany rezultat** | Strona zwraca kod `200 OK`. Wyświetlane są 3 plany: Starter (`49.00 PLN`, 1000 req), Professional (`149.00 PLN`, 5000 req) oraz Enterprise (`499.00 PLN`, 25000 req). Układ jest responsywny i czytelny. |

---

### Przypadek testowy TC002
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC002` |
| **Tytuł** | Dynamiczne przeliczenie proporcjonalnej migracji w kalkulatorze (upgrade Starter -> Professional w połowie cyklu) |
| **Warunki początkowe** | Użytkownik znajduje się na stronie głównej `http://127.0.0.1:5000/`. |
| **Kroki testowe** | 1. Przewiń widok do sekcji "Kalkulator proporcjonalnego rozliczenia (Proration)".<br>2. W polu "Obecny plan" wybierz `Starter (49.00 PLN)`.<br>3. W polu "Nowy plan" wybierz `Professional (149.00 PLN)`.<br>4. W polu "Dzień zmiany w cyklu" wprowadź wartość `15`.<br>5. W polu "Długość cyklu" pozostaw domyślną wartość `30`.<br>6. Kliknij przycisk "Przelicz rozliczenie". |
| **Oczekiwany rezultat** | Aplikacja bez przeładowania strony (AJAX) prezentuje wynik kalkulacji:<br>- Niewykorzystany kredyt ze starego planu: `24.50 PLN`<br>- Koszt nowego planu za pozostały okres: `74.50 PLN`<br>- Kwota netto do dopłaty: `50.00 PLN`<br>- Saldo kredytowe: `0.00 PLN`. |

---

### Przypadek testowy TC003
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC003` |
| **Tytuł** | Blokada kalkulacji proration przy przekroczeniu długości cyklu rozliczeniowego |
| **Warunki początkowe** | Użytkownik znajduje się na stronie głównej `http://127.0.0.1:5000/`. |
| **Kroki testowe** | 1. W sekcji kalkulatora proration wybierz obecny plan `Starter` i plan docelowy `Professional`.<br>2. W polu "Dzień zmiany w cyklu" wprowadź wartość `35` (przy długości cyklu `30`).<br>3. Kliknij przycisk "Przelicz rozliczenie" lub wyślij żądanie POST do `/api/proration/calculate`. |
| **Oczekiwany rezultat** | Aplikacja odrzuca żądanie ze statusem `422 Unprocessable Entity` i wyświetla komunikat błędu informujący, że dzień zmiany nie może przekraczać łącznej liczby dni w cyklu. |

---

### Przypadek testowy TC004
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC004` |
| **Tytuł** | Rejestracja nowej subskrypcji przez formularz interfejsu użytkownika |
| **Warunki początkowe** | Użytkownik znajduje się na stronie głównej `http://127.0.0.1:5000/`. |
| **Kroki testowe** | 1. Zlokalizuj formularz "Aktywuj nową subskrypcję".<br>2. W polu "Identyfikator klienta" wpisz `acme-corp`.<br>3. W liście rozwijanej "Wybierz plan" wybierz `Professional (149.00 PLN)`.<br>4. Kliknij przycisk "Utwórz i aktywuj subskrypcję". |
| **Oczekiwany rezultat** | Formularz wysyła żądanie `POST /subscriptions`. Następuje przekierowanie `302` do `/`. W tabeli "Zarejestrowane subskrypcje" pojawia się nowy wiersz z klientem `acme-corp`, planem `Professional`, statusem `ACTIVE` i zielonym znacznikiem aktywności. |

---

### Przypadek testowy TC005
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC005` |
| **Tytuł** | Walidacja pustego identyfikatora klienta przy tworzeniu subskrypcji |
| **Warunki początkowe** | Użytkownik znajduje się na stronie głównej `http://127.0.0.1:5000/`. |
| **Kroki testowe** | 1. Pozostaw pole "Identyfikator klienta" całkowicie puste.<br>2. Wybierz dowolny plan z listy rozwijanej (np. `Starter`).<br>3. Kliknij przycisk "Utwórz i aktywuj subskrypcję" (lub wyślij bezpośrednie żądanie POST z pustym polem). |
| **Oczekiwany rezultat** | Formularz blokuje wysłanie (walidacja HTML5 `required`) lub serwer zwraca kod błędu `400 Bad Request` z komunikatem `"Brakujące wymagane pola customer_id lub plan_tier"`. Żadna nowa subskrypcja nie zostaje utworzona. |

---

### Przypadek testowy TC006
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC006` |
| **Tytuł** | Przeprowadzenie migracji taryfy subskrypcji z poziomu tabeli zarządczej |
| **Warunki początkowe** | W systemie istnieje aktywna subskrypcja klienta `acme-corp` z taryfą `Starter`. |
| **Kroki testowe** | 1. W wierszu subskrypcji klienta `acme-corp` zlokalizuj pole wyboru "Zmień plan".<br>2. Wybierz plan docelowy `Enterprise`.<br>3. Kliknij przycisk "Zmień". |
| **Oczekiwany rezultat** | Żądanie `POST /subscriptions/<id>/migrate` zostaje przetworzone pomyślnie. Strona odświeża się (`302`). Wiersz klienta `acme-corp` wyświetla teraz plan `Enterprise`, a system przelicza proporcjonalnie saldo rozliczenia. |

---

### Przypadek testowy TC007
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC007` |
| **Tytuł** | Wyświetlenie i weryfikacja wizualnej faktury rozliczeniowej dla subskrypcji |
| **Warunki początkowe** | W systemie istnieje aktywna subskrypcja (np. o identyfikatorze `sub-001`). |
| **Kroki testowe** | 1. W tabeli subskrypcji kliknij przycisk "Faktura" przy wybranej subskrypcji (lub przejdź pod adres `http://127.0.0.1:5000/subscriptions/sub-001/invoice`).<br>2. Zweryfikuj nagłówek dokumentu, identyfikator faktury, dane klienta oraz datę wystawienia.<br>3. Sprawdź pozycje na fakturze: abonament bazowy oraz naliczone opłaty za zapytania API.<br>4. Sprawdź obecność przycisku powrotu do panelu głównego. |
| **Oczekiwany rezultat** | Serwer zwraca stronę faktury z kodem `200 OK`. Dokument zawiera dokładne zestawienie pozycji rozliczeniowych, formatowane kwoty w `PLN`, status opłacenia oraz link powrotny do Dashboardu. |

---

### Przypadek testowy TC008
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC008` |
| **Tytuł** | Anulowanie subskrypcji i weryfikacja zmiany statusu w maszynie stanów |
| **Warunki początkowe** | W systemie istnieje aktywna subskrypcja o statusie `ACTIVE`. |
| **Kroki testowe** | 1. W tabeli subskrypcji odszukaj aktywną pozycję.<br>2. Kliknij czerwony przycisk "Anuluj".<br>3. Potwierdź chęć anulowania i poczekaj na przeładowanie strony. |
| **Oczekiwany rezultat** | Serwer przetwarza żądanie `POST /subscriptions/<id>/cancel`. Status subskrypcji zmienia się na `CANCELLED` (szary badge). Przyciski zmiany planu oraz anulowania stają się nieaktywne lub zablokowane, uniemożliwiając modyfikację anulowanej umowy. |

---

### Przypadek testowy TC009
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC009` |
| **Tytuł** | Bezpośrednie pobranie katalogu taryf przez REST API (`GET /api/plans`) |
| **Warunki początkowe** | Aplikacja uruchomiona, narzędzie curl lub przeglądarka dostępne. |
| **Kroki testowe** | 1. Wykonaj w terminalu żądanie: `curl -s -X GET http://127.0.0.1:5000/api/plans -H "Accept: application/json"`.<br>2. Zweryfikuj kod statusu HTTP odpowiedzi.<br>3. Zweryfikuj nagłówek `Content-Type`.<br>4. Zweryfikuj strukturę tablicy obiektów JSON oraz obecność pól: `tier`, `name`, `base_price`, `currency`, `included_requests`. |
| **Oczekiwany rezultat** | Status odpowiedzi to `200 OK`. `Content-Type` to `application/json`. Zwrócona tablica zawiera 3 poprawne obiekty JSON odpowiadające taryfom Starter, Professional i Enterprise z poprawnymi cenami bazowymi. |

---

### Przypadek testowy TC010
| Pole | Wartość |
| :--- | :--- |
| **ID** | `TC010` |
| **Tytuł** | Próba otwarcia faktury dla nieistniejącej subskrypcji (`404 Not Found`) |
| **Warunki początkowe** | Aplikacja uruchomiona pod adresem `http://127.0.0.1:5000/`. |
| **Kroki testowe** | 1. Wprowadź w pasku adresu przeglądarki URL: `http://127.0.0.1:5000/subscriptions/sub-nieistnieje-999/invoice`.<br>2. Naciśnij klawisz Enter.<br>3. Zweryfikuj kod odpowiedzi HTTP i treść strony. |
| **Oczekiwany rezultat** | Serwer zwraca kod błędu `404 Not Found` z komunikatem JSON: `{"error": "Subskrypcja nie istnieje"}`. Aplikacja nie rzuca nieobsłużonego wyjątku `500 Internal Server Error`. |

---

## Technologie użyte w projekcie
* **Język programowania:** Python 3.12
* **Framework webowy:** Flask 3.1
* **Styling & UI:** Tailwind CSS (CDN), Inter Font, JetBrains Mono
* **Arytmetyka finansowa:** `decimal.Decimal` (precyzja walutowa, brak błędów `float`)
* **Testowanie:** `unittest` (konwencja AAA), `unittest.mock`
* **Analiza jakości:** `coverage.py` (badanie branch coverage)
* **Kontrola wersji:** Git / GitHub
