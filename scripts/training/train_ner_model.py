import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
import pandas as pd
from scripts.utils.tech_extractor import extract_tech_stack

df = pd.read_csv(
    os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv'),
    sep=';',
    encoding='utf-8'
)

df['tech_stack'] = df['full_text'].apply(extract_tech_stack)
df.to_csv(os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv'),
          sep=';', index=False, encoding='utf-8')

print('Технологические стеки извлечены')
print(df['tech_stack'].head())