import pandas as pd

#1.free press index
fp_id = pd.read_csv('world_press_freedom_index.csv')
fp_id.drop(['Unnamed: 0'], axis=1, inplace=True)
fp_id.columns = (
    fp_id.columns
    .str.strip()
    .str.replace(r'\n', '', regex=True)
    .str.replace(r'\[.*\]', '', regex=True)
)
fp_id = fp_id.replace(r'\(.*\)', '', regex=True)
#press_id = fp_id.apply(pd.to_numeric, errors='ignore')
fp_id = pd.melt(
    fp_id,
    id_vars=['Country'],
    var_name='Year',
    value_name='freepress'
)

print(fp_id.head())

#2.fredoom index
free_id = pd.read_csv('freedom_index.csv')
free_id.drop(
    [
        'Unnamed: 0', 'Region',
        'Property Rights', 'Government Integrity', 'Judicial Effectiveness',
        'Tax Burden', 'Government Spending', 'Fiscal Health',
        'Business Freedom', 'Labor Freedom', 'Monetary Freedom',
        'Trade Freedom', 'Investment Freedom', 'Financial Freedom'
    ],
    axis=1,
    inplace=True
)
free_id.columns = (
    free_id.columns. str.replace(r'Overall Score', 'freedoom', regex=True))
print(free_id.head())

#3.gpd
gpd_id = pd.read_csv('world_gdp_data.csv', encoding='cp1250')
gpd_id = gpd_id.rename({'Annual GDP growth (percent change)': 'GPD'})
gpd_id = gpd_id.melt(
    id_vars=['country_name'],        # kolumna, która ma pozostać jako identyfikator
    value_vars=[str(y) for y in range(1980, 2025)],  # kolumny lat jako wartości
    var_name='year',                  # nowa kolumna z nazwą roku
    value_name='gdp'                 # nowa kolumna z wartościami GDP
)

print(gpd_id.head())


#pomoce
# print(free_id.shape)
# print(free_id.columns.tolist())
# print(free_id.head(2))