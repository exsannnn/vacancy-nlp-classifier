from scripts.utils.hh_api import fetch_vacancies_search
import pandas as pd
import config
import time
import os

main_csv = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

df = pd.read_csv(main_csv, sep=';', encoding='utf-8')
existing_ids = set(df['id'].astype(str).tolist())

def fetch_new_vacancies():
    new_vacancies = []
    for query in ['machine learning', 'data science', 'python developer']:
        params = {
            "text": query,
            "area": 113,
            "per_page": 20,
            "page": 0
        }
        data = fetch_vacancies_search(params)
        if data is None:
            continue
        for item in data.get('items', []):
            if str(item['id']) in existing_ids:
                continue
            vacancy = {
                'id': item['id'],
                'name': item['name'],
                'full_text': f"{item['name']}. {item.get('snippet', {}).get('requirement', '')} {item.get('snippet', {}).get('responsibility', '')}",
                'category': '',
                'level': '',
                'skills': '',
                'notes': '',
                'quality_score': '',
                'tech_stack': '',
                'scam_flag': ''
            }
            new_vacancies.append(vacancy)
            existing_ids.add(str(item['id']))
        time.sleep(0.5)
    return new_vacancies

new = fetch_new_vacancies()
if new:
    df_new = pd.DataFrame(new)
    df_combined = pd.concat([df, df_new])
    df_combined.to_csv(main_csv, sep=';', index=False, encoding='utf-8')
    print(f'Добавлено {len(new)} новых вакансий')
else:
    print('Новых вакансий нет')