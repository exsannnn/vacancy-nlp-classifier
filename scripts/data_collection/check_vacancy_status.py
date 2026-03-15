from scripts.utils.hh_api import safe_request
import pandas as pd
import config
import os
import time

csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

df = pd.read_csv(csv_path, sep=';')

if 'status' not in df.columns:
    df['status'] = 'unknown'

archived_count = 0
checked_count = 0

for index, row in df.iterrows():
    if row['status'] == 'archived':
        continue
    vacancy_id = row['id']
    url = f'https://api.hh.ru/vacancies/{vacancy_id}'
    response = safe_request(url)
    checked_count += 1
    if response is None:
        continue
    if response.status_code == 404:
        df.at[index, 'status'] = 'archived'
        archived_count += 1
    else:
        data = response.json()
        if data.get('archived') == True or data.get('status') == 'archived':
            df.at[index, 'status'] = 'archived'
            archived_count += 1
        else:
            df.at[index, 'status'] = 'active'
    time.sleep(0.2)

df.to_csv(csv_path, sep=';', index=False)
print(f"Проверено {checked_count} вакансий, найдено {archived_count} архивных")