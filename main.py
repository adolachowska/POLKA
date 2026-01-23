import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

#funkcje
def scaling(s, lower_q=0.005, upper_q=0.995):
    #Winsorization
    if s.dropna().empty: #check NaN
        return pd.Series(index=s.index, dtype=float)
    min = s.quantile(lower_q) #kwarcyle
    max = s.quantile(upper_q)
    s_clip = s.clip(lower=min, upper=max) #ucięcie
    denom = (max - min) if (max - min) != 0 else 1.0 #scalowanie do max i min
    return (s_clip - min) / denom

"""
#test scaling
cols = [
    "press_free",
    "electoral_integrity",
    "judicial_independence",
    "civil_liberties",
    "gov_stability",
    "absence_of_violence"
]
df[cols] = df[cols].apply(scaling)
print(df.head())
"""

def safe_mean_weighted(df, cols, weights):#wagowanie

    data_to_mean = df[cols].values.astype(float)
    valid = ~np.isnan(data_to_mean) #if True NaN
    w = np.array(weights)[None, :]
    weighted_sum = np.nansum(data_to_mean * w * valid, axis=1)
    used_weights_sum = np.nansum(w * valid, axis=1)
    # Jeśli suma wag = 0 (wszystko NaN), ustaw NaN
    # used_weights_sum = np.where(used_weights_sum == 0, np.nan, used_weights_sum)
    # średnią ważona (nie dane Nan): suma danych po zastosowaniu wag/ suma zastosowanych wag
    return weighted_sum / used_weights_sum

"""
#test safe_mean_weighted
cols = [
    "press_free",
    "electoral_integrity",
    "judicial_independence",
    "civil_liberties",
    "gov_stability",
    "absence_of_violence"
]
weights = [1,1,1,1,1,1]
df["mean_weighted"] = safe_mean_weighted(df, cols, weights)
print(df.head())
"""

#przygotowanie danych do analizy
def compute_psi(
    df,
    components,
    weights=None,
    invert=None, #higher value
    scale_max=10.0, #scale_max: 10.0 -> result in [0,10]
    lower_q=0.005,
    upper_q=0.995,
    if_region=None #do scaling per group
):
    if invert is None:
        invert = [] #always list
    if weights is None: #no weights
        weights = [1.0/len(components)] * len(components)
    assert len(weights) == len(components), "Weights must match columns" #jedna waga jeden

    df = df.copy()
    #
    scaled_cols = [] #ready variable to modify

    # normalization: global or by group
    if if_region is None:
        # global
        for c in components:
            scaled_name = f"{c}_scaled"
            df[scaled_name] = scaling(df[c], lower_q, upper_q)
            if c in invert:
                df[scaled_name] = 1.0 - df[scaled_name]
            scaled_cols.append(scaled_name)
    else:
        # regional
        scaled_cols = []
        for c in components:
            scaled_name = f"{c}_scaled"
            df[scaled_name] = np.nan
            for g, sub in df.groupby(if_region):
                df.loc[sub.index, scaled_name] = scaling(sub[c], lower_q, upper_q)
            if c in invert:
                df[scaled_name] = 1.0 - df[scaled_name]
            scaled_cols.append(scaled_name)

    # weighted
    df['p_raw'] = safe_mean_weighted(df, scaled_cols, weights)
    df['p'] = df['p_raw'] * scale_max #skalujemy

    return df

"""

def add_p_lags(df, lags=(1, 3, 5)): #spradzanie przejścia lag
    df = df.sort_values(["country", "year"])
    for l in lags:
        df[f"p_lag_{l}"] = df.groupby("country")["p"].shift(l) #shift przesuwa o liczbę wierszy (l) w dół kolumnę
    return df


def add_p_trend(df, window=5): # 5 year trend
    df = df.sort_values(["country", "year"])
    df["p_trend"] = (
        df.groupby("country")["p"]
        .rolling(window) #przesuwa o trend
        .apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        .reset_index(level=0, drop=True)
    )
    return df
"""

def to_regime(p):
    if pd.isna(p):
        return None
    if p < 0.3:
        return "autocracy"
    elif p < 0.5:
        return "hybrid"
    elif p < 0.7:
        return "flawed_democracy"
    else:
        return "democracy"

if __name__ == "__main__":
    components = [
        "press_free",
        "electoral_integrity",
        "judicial_independence",
        "civil_liberties",
        "gov_stability",
        "absence_of_violence"
    ]

    df = compute_psi(
        df=df,
        components=components,
        invert=[],  # np. ["absence_of_violence"] jeśli odwrotnie
        scale_max=1.0
    )

    df["regime_class"] = df["p"].apply(to_regime)

    df = add_p_lags(df)
    df = add_p_trend(df)

    print(
        df[
            [
                "country",
                "year",
                "p",
                "regime_class",
                "p_lag_1",
                "p_trend"
            ]
        ]
    )

#nasza predykcja

features = ["p_lag_1", "p_lag_3", "p_trend"]
target = "p"

df_model = df.dropna(subset=features + [target])

# sortowanie czasowe
df_model = df_model.sort_values(["country", "year"])

X = df_model[features]
y = df_model[target]

split = int(len(df_model) * 0.8) #0.8 historia, 0.2 czas

X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("MSE:", mean_squared_error(y_test, y_pred))
print("Współczynniki:", dict(zip(features, model.coef_)))
print("Intercept:", model.intercept_)


plt.figure(figsize=(8,4))
plt.plot(y_test.values, label="PSI rzeczywiste", marker="o")
plt.plot(y_pred, label="PSI przewidziane", marker="x")
plt.legend()
plt.title("Predykcja PSI")
plt.show()