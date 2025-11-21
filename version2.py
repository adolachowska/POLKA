
import pandas as pd
import wbgapi as wb
import pycountry

#GPD
gdp = wb.data.DataFrame('NY.GDP.MKTP.CD', time=range(1984,2025))
gdp = gdp.reset_index().rename(columns={'economy': 'country'})
gdp_long = gdp.melt(id_vars=['country'], var_name='year', value_name='gdp')
gdp_long['year'] = gdp_long['year'].str.replace('YR','').astype(int)

# --- Unemployment ---
unemp = wb.data.DataFrame('SL.UEM.TOTL.ZS', time=range(1984,2025))
unemp = unemp.reset_index().rename(columns={'economy': 'country'})
unemp_long = unemp.melt(id_vars=['country'], var_name='year', value_name='unemployment')
unemp_long['year'] = unemp_long['year'].str.replace('YR','').astype(int)

# --- Conflict ---
conflict = pd.read_csv(r"C:\Users\ali\Desktop\POLKA\UcdpPrioConflict_v25_1.csv")
conflict = conflict[["year", "location"]].dropna()

