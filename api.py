from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import numpy as np
from io import StringIO
import csv
import codecs

"""
plan API
klasa model kraj 
podając rok musisz przyporządkować parametry
obl współczynnika p jako część klasy
parametry osobną klasą
API → wskaźniki → model domenowy → liczy p → zapis
"""

#typy danych do Pydantic
class CountryCreate(BaseModel):
    name: str

class PoliticalIndicators(BaseModel):
    press_free: float
    electoral_integrity: float
    judicial_independence: float
    civil_liberties: float
    gov_stability: float
    absence_of_violence: float

class YearCreate(BaseModel):
    year: int
    indicators: PoliticalIndicators

#model wewnątrz
class Country:
    def __init__(self, name: str):
        self.name = name
        self.data = pd.DataFrame(columns=[
            "year",
            "press_free",
            "electoral_integrity",
            "judicial_independence",
            "civil_liberties",
            "gov_stability",
            "absence_of_violence",
            "p",
            "p_lag_1",
            "p_lag_3",
            "p_trend"
        ])

    def _compute_p(self, indicators: dict) -> float:
        values = np.array(list(indicators.values()), dtype=float)
        return float(values.mean())

    def _recompute_features(self):
        self.data = self.data.sort_values("year").reset_index(drop=True) #nowy index po datach

        self.data["p_lag_1"] = self.data["p"].shift(1)
        self.data["p_lag_3"] = self.data["p"].shift(3)

        if len(self.data) >= 5:
            self.data["p_trend"] = (
                self.data["p"]
                .rolling(5)
                .apply(lambda x: x.iloc[-1] - x.iloc[0]) #sugestia: współczynnik zmiany w trakcie 65 lat, nie różnica między 5 latami, nie widzi zmian rok do rok, do zmiany
            )
        else:
            self.data["p_trend"] = np.nan

    def model_add_year(self, year: int, indicators: PoliticalIndicators):
        if year in self.data["year"].values:
            raise ValueError("Year already exists")

        indicators_dict = indicators.dict() #zamiana na pliki python
        p = self._compute_p(indicators_dict)

        row = {
            "year": year,
            **indicators_dict, #każda kolumna osobno
            "p": p,
            "p_lag_1": None,
            "p_lag_3": None,
            "p_trend": None
        }
        self.data.loc[len(self.data)] = row #zapis całego wiersza po numerze wiersza
        self._recompute_features()



COUNTRIES: dict[str, Country] = {}

def create_country(name: str):
    if name in COUNTRIES:
        raise ValueError("Country already exists")
    COUNTRIES[name] = Country(name)


def delete_country(name: str):
    if name not in COUNTRIES:
        raise ValueError("Country not found")
    del COUNTRIES[name]


def get_country(name: str): #already in API?
    if name not in COUNTRIES:
        raise ValueError("Country not found")
    return COUNTRIES[name]


def list_countries():
    return list(COUNTRIES.keys())


router = APIRouter()
@router.post("/countries")
def api_create_country(payload: CountryCreate):
    try:
        create_country(payload.name)
        return {"status": "created", "country": payload.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/countries/{name}")
def api_delete_country(name: str):
    try:
        delete_country(name)
        return {"status": "deleted", "country": name}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/countries/{name}/year")
def api_add_year(name: str, payload: YearCreate):
    try:
        country = get_country(name)
        country.model_add_year(payload.year, payload.indicators)
        return {"status": "year added", "year": payload.year}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/countries")
def api_list_countries():
    return list_countries()


@router.get("/countries/{name}")
def api_get_country_data(name: str):
    try:
        country = get_country(name)
        return country.data.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/countries/{name}/upload-csv")
def upload_csv(
    name: str,
    file: UploadFile = File(...)):

    country = get_country(name)

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Not CSV file")

    reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    # zamiana surowego strumienia bajtów "file" na tekst "utf-8"

    required_columns = [
        "country"
        "year",
        "press_free",
        "electoral_integrity",
        "judicial_independence",
        "civil_liberties",
        "gov_stability",
        "absence_of_violence"]

    if not required_columns.issubset(reader.fieldnames):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {required_columns}"
        )

    years_added = 0

    for row in reader:
        indicators = PoliticalIndicators(
            press_free=float(row["press_free"]),
            electoral_integrity=float(row["electoral_integrity"]),
            judicial_independence=float(row["judicial_independence"]),
            civil_liberties=float(row["civil_liberties"]),
            gov_stability=float(row["gov_stability"]),
            absence_of_violence=float(row["absence_of_violence"]),
        )

        country.model_add_year(
            year=int(row["year"]),
            indicators=indicators
        )

        years_added += 1

    return {
        "status": "csv uploaded",
        "rows_added": years_added
    }

    file.file.close()

app = FastAPI(title="POLKA – Political System Forecast API")
app.include_router(router)