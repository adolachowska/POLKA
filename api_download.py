import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

def fetch_full_dataframe():
    print("📡 Downloading API...")

    try:
        response_list = requests.get(f"{BASE_URL}/countries")
        if response_list.status_code != 200:
            raise Exception(f"Download failed: {response_list.status_code}")

        countries_list = response_list.json()
        print(f"🌍 Countries list: {len(countries_list)}")

    except Exception as e:
        print(f"❌ Problem: {e}")
        return pd.DataFrame()

    all_data_frames = []

    for item in countries_list:
        country_name = item['name']
        get_data = requests.get(f"{BASE_URL}/countries/{country_name}")

        if get_data.status_code == 200:
            details = get_data.json()

            if 'data' in details and details['data']:
                df_temp = pd.DataFrame(details['data'])
                df_temp['Country'] = country_name
                all_data_frames.append(df_temp)
        else:
            print(f"⚠️ Failed download for: {country_name}")

    if all_data_frames:
        full_df = pd.concat(all_data_frames, ignore_index=True)
        full_df['year'] = pd.to_numeric(full_df['year'])
        full_df = full_df.sort_values(by=['Country', 'year']).reset_index(drop=True)
        print(f"✅ Downloaded {len(full_df)} records.")
        return full_df
    else:
        print("❌ No files downloaded")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_full_dataframe()
    print(df.head())

