import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Wczytanie danych
df = pd.read_csv("political_data.csv", parse_dates=["date"])
df = df.sort_values("date")
df = df.set_index("date")

# Funkcja dodająca cechy rolling i delta
def add_features_yearly(df, col, window=3):
    df[f"{col}_rolling"] = df.groupby("country")[col].transform(lambda x: x.rolling(window=window).mean())
    df[f"{col}_delta"] = df.groupby("country")[col].transform(lambda x: x.diff(1))
    return df

for col in ["freepress", "gdp", "unemployment", "conflict"]:
    df = add_features_yearly(df, col)

# Filtrujemy tylko Serbię
df_serbia = df[df["country"] == "Serbia"].dropna()

# Wybór cech
features = [
    "freepress_rolling", "freepress_delta",
    "gdp", "gdp_rolling", "gdp_delta",
    "unemployment", "unemployment_rolling",
    "conflict", "conflict_rolling"
]

X = df_serbia[features]
y = df_serbia["freepress"]

# Podział na trening i test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Model regresji liniowej
model = LinearRegression()
model.fit(X_train, y_train)

# Predykcja
y_pred = model.predict(X_test)

# Ewaluacja
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))

# Wykres rzeczywiste vs przewidziane wartości
plt.figure(figsize=(10,5))
plt.plot(y_test.index, y_test, label="Rzeczywiste wartości", marker="o")
plt.plot(y_test.index, y_pred, label="Przewidywane wartości", marker="x")
plt.title("Predykcja wartości freepress dla Serbii")
plt.legend()
plt.show()

# Predykcja dla nowego zestawu danych Serbii
new_data_serbia = pd.DataFrame([{
    "freepress_rolling": 68,
    "freepress_delta": -2,
    "gdp": 85,
    "gdp_rolling": 80,
    "gdp_delta": 2,
    "unemployment": 8,
    "unemployment_rolling": 7.5,
    "conflict": 1.9,
    "conflict_rolling": 1.8
}])

print("Predykcja freepress dla nowego przypadku w Serbii:", model.predict(new_data_serbia))