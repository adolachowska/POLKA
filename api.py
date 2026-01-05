from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd

#typy danych do Pydantic
class CountryCreate(BaseModel):
    name: str

class YearCreate(BaseModel):
    year: int
    p: float

#model wewnątrz
class Country:
    def __init__(self, name: str):
        self.name = name
        self.data = pd.DataFrame(
            columns=["year", "p", "p_lag_1", "p_lag_3", "p_trend"]
        )

    def model_add_year(self, year: int, p: float): #przechowuje dane w ramach klasy self, model operacji liczenia współczynników p

        if year in self.data["year"].values:
            raise ValueError("Year already exists")

        self.data.loc[len(self.data)] = {
            "year": year,
            "p": p,
            "p_lag_1": None,
            "p_lag_3": None,
            "p_trend": None
        }
        self._recompute_features()

    def _recompute_features(self):
        self.data = self.data.sort_values("year").reset_index(drop=True)
        self.data["p_lag_1"] = self.data["p"].shift(1)
        self.data["p_lag_3"] = self.data["p"].shift(3)

        if len(self.data) >= 5:
            self.data["p_trend"] = (
                self.data["p"]
                .rolling(5)
                .apply(lambda x: x.iloc[-1] - x.iloc[0])
            )
        else:
            self.data["p_trend"] = None


#kraje
COUNTRIES: dict[str, Country] = {}

def create_country(name: str):
    if name in COUNTRIES:
        raise ValueError("Country already exists")
    COUNTRIES[name] = Country(name)

def delete_country(name: str):
    if name not in COUNTRIES:
        raise ValueError("Country not found")
    del COUNTRIES[name]

def get_country(name: str) -> Country:
    if name not in COUNTRIES:
        raise ValueError("Country not found")
    return COUNTRIES[name]

def list_countries():
    return list(COUNTRIES.keys())

#router
router = APIRouter()

@router.post("/countries")
def add_country(payload: CountryCreate):
    try:
        create_country(payload.name)
        return {"status": "created", "country": payload.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/countries/{name}")
def remove_country(name: str):
    try:
        delete_country(name)
        return {"status": "deleted", "country": name}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/countries/{name}/year")
def add_year(name: str, payload: YearCreate):
    try:
        country = get_country(name)
        country.model_add_year(payload.year, payload.p)
        return {"status": "year added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/countries")
def get_countries():
    return list_countries()

@router.get("/countries/{name}")
def get_country_data(name: str):
    try:
        country = get_country(name)
        return country.data.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# aplikacja
app = FastAPI(title="POLKA API")
app.include_router(router)