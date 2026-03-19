import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Brakuje DATABASE_URL w pliku .env!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CountryDB(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)

    years = relationship("YearDataDB", back_populates="country", cascade="all, delete-orphan")


class YearDataDB(Base):
    __tablename__ = "political_data"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("CountryDB", back_populates="years")


    press_free = Column(Float)
    freedom_index = Column(Float)
    gdp = Column(Float)
    absence_of_violence = Column(Float)
    civil_liberties = Column(Float)
    gov_stability = Column(Float)
    human_rights = Column(Float)
    electoral_integrity = Column(Float)
    system_index = Column(Float)


    p = Column(Float)
    p_lag_1 = Column(Float, nullable=True)
    p_lag_3 = Column(Float, nullable=True)
    p_trend = Column(Float, nullable=True)


Base.metadata.create_all(bind=engine) #połączenie z Azune, tworzenie kolumn, komenda,