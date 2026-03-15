import pandas as pd
import shutil
import config
import os

csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

backup_path = csv_path.replace('.csv', '_backup.csv')
shutil.copy2(csv_path, backup_path)

df = pd.read_csv(csv_path, sep=';', encoding='utf-8')

category_map = {
    'ml': ['ml', 'ml_engineer', 'mlops', 'ml_ops', 'ai_dev', 'ml_rl', 'ml_architect'],
    'data': ['data', 'data_scientist', 'data_analytics_lead', 'data_intern'],
    'backend': ['backend', 'python_dev_data', 'python_senior', 'python_mid'],
    'nlp': ['nlp'],
    'cv': ['cv'],
    'analytics': ['analytics', 'analyst', 'product'],
    'other': ['sales', 'systems', 'bizdev', 'fullstack', 'operations', 'generalist', 'hr', 'marketing']
}

level_map = {
    'junior': ['junior', 'intern'],
    'middle': ['middle', 'junior-middle'],
    'senior': ['senior', 'middle-senior', 'lead', 'Middle+/Senior', 'Middle/Senior']
}

def map_category(cat):
    cat = str(cat).lower().strip()
    for main_cat, variants in category_map.items():
        if cat in variants:
            return main_cat
    return 'other'

def map_level(lvl):
    lvl = str(lvl).lower().strip()
    for main_lvl, variants in level_map.items():
        if lvl in variants:
            return main_lvl
    return 'unknown'

df['category'] = df['category'].apply(map_category)
df['level'] = df['level'].apply(map_level)

df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
print(f'Уникальные категории: {df["category"].unique()}')
print(f'Уникальные уровни: {df["level"].unique()}')
print(f'Файл {csv_path} обновлён, бэкап сохранён как {backup_path}')