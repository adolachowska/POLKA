import pandas as pd

"""
1. free_press
2. freedoom_index
3. gpd
4. absence_of_violence
5. civil_liberties
6. gov_stability
7. human_rights
8. electoral_integrity
"""

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
#print(fp_id.head())


#2.freedoom index
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
#print(free_id.head())


#3.gpd
gpd_id = pd.read_csv('world_gdp_data.csv', encoding='cp1250')
gpd_id = gpd_id.rename({'Annual GDP growth (percent change)': 'GPD'})
gpd_id = gpd_id.melt(
    id_vars=['country_name'],        # kolumna, która ma pozostać jako identyfikator
    value_vars=[str(y) for y in range(1980, 2025)],  # kolumny lat jako wartości
    var_name='Year',                  # nowa kolumna z nazwą roku
    value_name='gdp'                 # nowa kolumna z wartościami GDP
)
#print(gpd_id.head())


#4.Political Stability and Absence of Violence/Terrorism: Percentile Rank
#https://data.worldbank.org/indicator/PV.PER.RNK
absence_of_violence_id = pd.read_csv(
    'absence_of_violence.csv',
    skiprows=4,
    engine='python'
)

bsence_of_violence_id = absence_of_violence_id.drop(
    [
        'Country Code',
        'Indicator Name',
        'Indicator Code',
        'Unnamed: 69'
    ],
    axis=1
)
absence_of_violence_id = absence_of_violence_id.rename(columns={'Country Name': 'Country'})

absence_of_violence_id = absence_of_violence_id.melt(
    id_vars=['Country'],
    value_vars=[str(y) for y in range(1960, 2024)],  # kolumny lat jako wartości
    var_name='Year',                  # nowa kolumna z nazwą roku
    value_name='absence_of_violence'                 # nowa kolumna z wartościami GDP
)
#print(absence_of_violence_id.head(10))


#5 civil_liberties
#https://ourworldindata.org/grapher/civil-liberties-index-eiu
civil_liberties_id = pd.read_csv(
    'civil-liberties-index-eiu.csv',
    engine='python'
)
civil_liberties_id.drop(['World region according to OWID','Code'], axis=1, inplace=True)
civil_liberties_id = civil_liberties_id.rename(columns={'Entity': 'Country'})
civil_liberties_id = civil_liberties_id.rename(columns={'Civil liberties': 'civil_liberties'})
#print(civil_liberties_id.head(10))

#6
#gov_stability
#Corruption perceptions
#https://www.transparency.org/en
#https://ourworldindata.org/grapher/ti-corruption-perception-index
cor_per_id = pd.read_csv('ti-corruption-perception-index.csv')
cor_per_id.rename(columns={
    'Entity': 'Country',
    'Corruption Perceptions Index': 'corruption_score'
}, inplace=True)

cor_per_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)
#print(cor_per_id.head(10))

#7
#human_rights
#https://ourworldindata.org/grapher/human-rights-index-vdem
hum_rig_id = pd.read_csv('human-rights-index-vdem.csv')
hum_rig_id.rename(columns={
    'Entity': 'Country',
    'Civil liberties index (central estimate)': 'human_rights'
}, inplace=True)
hum_rig_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)
#print(hum_rig_id.head(10))

# 8. electoral_integrity
# https://ourworldindata.org/grapher/electoral-democracy-index
ele_int_id = pd.read_csv('electoral-democracy-index.csv')
ele_int_id.rename(columns={
    'Entity': 'Country',
    'Electoral democracy index (central estimate)': 'electoral_integrity'
}, inplace=True)
ele_int_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)
print(ele_int_id.head(10))

#pomoce
# print(free_id.shape)
# print(free_id.columns.tolist())
# print(free_id.head(2))