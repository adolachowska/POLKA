from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic import BaseModel
import csv
from io import StringIO
from typing import Optional

from sql import SessionLocal, CountryDB, YearDataDB
from blob_service import upload_file_to_blob

app = FastAPI(title="POLKA – Political System Forecast API (Azure SQL Edition)")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PoliticalIndicators(BaseModel):
    press_free: Optional[float] = None
    freedom_index: Optional[float] = None
    gdp: Optional[float] = None
    absence_of_violence: Optional[float] = None
    civil_liberties: Optional[float] = None
    gov_stability: Optional[float] = None
    human_rights: Optional[float] = None
    electoral_integrity: Optional[float] = None
    system_index: Optional[float] = None


class YearCreate(BaseModel):
    year: int
    indicators: PoliticalIndicators


class CountryCreate(BaseModel):
    name: str


@app.post("/countries")
def create_country(payload: CountryCreate, db: Session = Depends(get_db)):
    existing = db.query(CountryDB).filter(CountryDB.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Country already exists")

    new_country = CountryDB(name=payload.name)
    db.add(new_country)
    db.commit()
    return {"status": "created", "country": payload.name}


@app.get("/countries")
def get_all_countries(db: Session = Depends(get_db)):
    countries = db.query(CountryDB).all()
    return [{"name": country.name} for country in countries]


@app.post("/countries/{name}/year")
def add_year(name: str, payload: YearCreate, db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    exists = db.query(YearDataDB).filter_by(country_id=country.id, year=payload.year).first()
    if exists:
        raise HTTPException(status_code=400, detail="Year already exists")

    new_data = YearDataDB(
        country_id=country.id,
        year=payload.year,
        **payload.indicators.model_dump()
    )
    db.add(new_data)
    db.commit()

    return {"status": "year added", "year": payload.year}


@app.get("/countries/{name}")
def get_country_data(name: str, db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    records = db.query(YearDataDB).filter_by(country_id=country.id).order_by(YearDataDB.year).all()

    data_list = []
    for r in records:
        row_dict = r.__dict__.copy()
        row_dict.pop('_sa_instance_state', None)
        data_list.append(row_dict)

    return {"data": data_list}


@app.post("/countries/{name}/upload-csv")
async def upload_csv(name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Not CSV file")

    file_content = await file.read()
    blob_url = await run_in_threadpool(upload_file_to_blob, file_content, file.filename)

    csv_text = file_content.decode("utf-8")
    reader = csv.DictReader(StringIO(csv_text))

    years_added = 0

    required_columns = {"year", "press_free", "freedom_index", "gdp", "absence_of_violence",
                        "electoral_integrity", "civil_liberties",
                        "gov_stability", "human_rights", "electoral_integrity", "system_index"}

    for col in required_columns:
        if col not in reader.fieldnames:
            raise HTTPException(status_code=400, detail=f"Missing column: {col}")

    for row in reader:
        try:
            # 1. BEZPIECZNE POBIERANIE ROKU
            year_str = str(row.get("year", "")).strip()
            # Jeśli brak roku lub rok to "nan", pomijamy całkowicie ten wiersz (jest bezużyteczny)
            if not year_str or year_str.lower() == "nan":
                continue

                # Konwersja do float, a potem int pozwala uniknąć błędu, gdy rok to np. "2020.0"
            year_val = int(float(year_str))

            # 2. BEZPIECZNA KONWERSJA WSKAŹNIKÓW
            def parse_val(v):
                if v is None:
                    return None
                val_str = str(v).strip().lower()
                if val_str == "" or val_str == "nan":
                    return None
                return float(v)

            indicators = PoliticalIndicators(
                press_free=parse_val(row.get("press_free")),
                freedom_index=parse_val(row.get("freedom_index")),
                gdp=parse_val(row.get("gdp")),
                absence_of_violence=parse_val(row.get("absence_of_violence")),
                civil_liberties=parse_val(row.get("civil_liberties")),
                gov_stability=parse_val(row.get("gov_stability")),
                human_rights=parse_val(row.get("human_rights")),
                electoral_integrity=parse_val(row.get("electoral_integrity")),
                system_index=parse_val(row.get("system_index")),
            )

            if not db.query(YearDataDB).filter_by(country_id=country.id, year=year_val).first():
                new_row = YearDataDB(
                    country_id=country.id,
                    year=year_val,
                    **indicators.model_dump()
                )
                db.add(new_row)
                years_added += 1

        except Exception as e:
            # Jeśli cokolwiek wybuchnie, serwer dokładnie powie nam dlaczego
            print(f"Skipping row due to error: {e} | Row: {row}")
            continue

    db.commit()

    return {
        "status": "csv uploaded and processed",
        "rows_added": years_added,
        "backup_url": blob_url
    }