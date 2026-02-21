<h1>Political Stability & Economic Indicators Predictor</h1>

An analytical and engineering project integrating data analysis (Data Science), API development (Backend), and Machine Learning to predict the political and economic stability indicators of countries.

**System Architecture (Data Pipeline)**

The project was designed around an automated data flow:

1. **Data Collection & Cleaning**: Fetching raw data from 8 different sources (including GDP, press freedom, and corruption indicators).
   - Cleaning, standardizing, and combining data (Data Merging) using the `pandas` library (utilizing `reduce` and outer join `pd.merge`).
2. **Backend & Data Storage (FastAPI + SQL)**: An automated Python "Robot" batches the cleaned data and sends it via HTTP (POST) to a custom API.
   - The API calculates a custom `p` indicator (the average of the base indicators), creates a backup in the cloud/Data Lake (Azurite), and then loads the data into a relational SQL database.
3. **Machine Learning Model**: The ML script always fetches the latest data directly from the SQL database using API requests (GET), bypassing local CSV files.
   - Conversion of the JSON format into NumPy vectors and matrices ready for model training.

**Technologies (Tech Stack)**
* Language: Python 3.x
* Data Processing: Pandas, NumPy, functools
* Backend: FastAPI, Uvicorn, Pydantic
* Database / Storage: SQL (e.g., SQLite/PostgreSQL), Azure Blob Storage (Azurite)
* Machine Learning: Scikit-Learn / Statsmodels 🔴 *(currently selecting the prediction model)* 🔴

**How to run the project locally?**

1. **Starting the API server**
In the terminal, navigate to the folder containing the `main.py` file and run the local server:
```bash
python -m uvicorn main:app --reload

The API will be available at: `http://127.0.0.1:8000`. Interactive Swagger documentation can be found at `/docs`.

2. **Data Ingestion**
Open the `data_analysis.ipynb` notebook and run all cells. 
At the end, the script will automatically connect to the API and send the cleaned historical data for all countries, loading it into the SQL database.

3. **Running the prediction model**
Run the prediction script (e.g., `prediction_model.ipynb` or an ML script). The script will fetch the integrated data from the API (the `/countries` endpoint) and start training the model.

**Repository Structure**
* `data_analysis.ipynb` - Data cleaning scripts (EDA).
* `api_download.ipynb` - Automated robot sending data to the API.
* `main.py` - Main FastAPI server file.
* `sql.py` - SQL database model definitions (SQLAlchemy).
* `blob_service.py` - Local data upload.
* `setup.py` - Creating local server (Azurite).

