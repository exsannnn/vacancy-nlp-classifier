from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import config
import pickle
import re
import os

data_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

df = pd.read_csv(data_path, sep=';', encoding='utf-8')

print(f'Загружено {len(df)} строк')

df['full_text'] = df['full_text'].fillna('')

def clean_text(text):
    text = str(text)
    text = text.lower()
    text = re.sub(r'[^а-яёa-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['clean_text'] = df['full_text'].apply(clean_text)

vectorizer = TfidfVectorizer(max_features=500)
X_text = vectorizer.fit_transform(df['clean_text'])

le_category = LabelEncoder()
y_category = le_category.fit_transform(df['category'])

le_level = LabelEncoder()
y_level = le_level.fit_transform(df['level'])

processed_dir = os.path.join(config.PROJECT_ROOT, 'data', 'processed')
models_basic_dir = os.path.join(config.PROJECT_ROOT, 'models', 'basic')

os.makedirs(processed_dir, exist_ok=True)
os.makedirs(models_basic_dir, exist_ok=True)

with open(os.path.join(processed_dir, 'X_text.pkl'), 'wb') as f:
    pickle.dump(X_text, f)

with open(os.path.join(processed_dir, 'y_category.pkl'), 'wb') as f:
    pickle.dump(y_category, f)

with open(os.path.join(processed_dir, 'y_level.pkl'), 'wb') as f:
    pickle.dump(y_level, f)

with open(os.path.join(models_basic_dir, 'vectorizer.pkl'), 'wb') as f:
    pickle.dump(vectorizer, f)

with open(os.path.join(models_basic_dir, 'le_category.pkl'), 'wb') as f:
    pickle.dump(le_category, f)

with open(os.path.join(models_basic_dir, 'le_level.pkl'), 'wb') as f:
    pickle.dump(le_level, f)

print('Готово!')
print(f'Категории: {le_category.classes_}')
print(f'Уровни: {le_level.classes_}')
print(f'Размер данных: {X_text.shape}')