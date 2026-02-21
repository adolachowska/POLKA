<h1>Political Stability & Economic Indicators Predictor</h1>

Projekt analityczno-inżynieryjny integrujący analizę danych (Data Science), tworzenie interfejsów API (Backend) oraz uczenie maszynowe (Machine Learning) w celu przewidywania wskaźników stabilności politycznej i gospodarczej państw.

Architektura Systemu (Data Pipeline)

Projekt został zaprojektowany w oparciu o zautomatyzowany przepływ danych:

1. Data Collection & Cleaning: Pobieranie surowych danych z 8 różnych źródeł (m.in. wskaźniki PKB, wolności prasy, korupcji).
   - Czyszczenie, ujednolicanie i łączenie danych (Data Merging) przy użyciu biblioteki `pandas` (wykorzystanie `reduce` i `pd.merge` typu outer join).
2. Backend & Data Storage (FastAPI + SQL):Zautomatyzowany "Robot" w Pythonie dzieli wyczyszczone dane i wysyła je via HTTP (POST) do autorskiego API.
   - API wylicza autorski wskaźnik `p` (średnia ze wskaźników bazowych), tworzy kopię zapasową w chmurze/Data Lake (Azurite), a następnie ładuje dane do relacyjnej bazy SQL.
3. Machine Learning Model: Skrypt ML pobiera zawsze najświeższe dane bezpośrednio z bazy SQL za pomocą zapytań API (GET), z pominięciem lokalnych plików CSV.
   - Konwersja formatu JSON na wektory i macierze NumPy gotowe do uczenia modelu.

**Technologie (Tech Stack)**
Język: Python 3.x
Data Processing: Pandas, NumPy, functools
Backend:F astAPI, Uvicorn, Pydantic
Baza Danych / Storage: SQL (np. SQLite/PostgreSQL), Azure Blob Storage (Azurite)
Machine Learning: Scikit-Learn / Statsmodels 🔴 (w trakcie wyboru modelu predykcji) 🔴

**Jak uruchomić projekt lokalnie?**

1. Uruchomienie serwera API
W terminalu przejdź do folderu z plikiem `main.py` i uruchom serwer lokalny:
```bash
python -m uvicorn main:app --reload
