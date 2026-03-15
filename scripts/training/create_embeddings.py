from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import config
import os

df = pd.read_csv(
    os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv'),
    sep=';',
    encoding='utf-8'
)

texts = df['full_text'].fillna('').tolist()

vectorizer = TfidfVectorizer(max_features=300)
embeddings = vectorizer.fit_transform(texts).toarray()

np.save(os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'embeddings.npy'), embeddings)

print(f'Эмбеддинги созданы: {embeddings.shape}')