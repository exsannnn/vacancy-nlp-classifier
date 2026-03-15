from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import config
import os

class RecommenderService:
    def __init__(self):
        csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')
        self.df = pd.read_csv(csv_path, sep=';', encoding='utf-8')

        if 'status' not in self.df.columns:
            self.df['status'] = 'active'

        self.active_df = self.df[self.df['status'] == 'active'].copy()
        if len(self.active_df) == 0:
            self.tfidf_matrix = None
            self.vectorizer = None
            return

        texts = self.active_df['full_text'].fillna('').tolist()
        self.vectorizer = TfidfVectorizer(max_features=500)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def recommend(self, query, top_k=5):
        if self.tfidf_matrix is None or len(self.active_df) == 0:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if idx >= len(self.active_df):
                continue
            row = self.active_df.iloc[idx]
            similarity = float(similarities[idx])
            if similarity < 0.1:
                continue
            results.append({
                'id': row['id'],
                'title': row['name'],
                'category': row['category'],
                'level': row['level'],
                'similarity': similarity
            })

        if len(results) == 0:
            top_k = min(top_k, len(self.active_df))
            sample = self.active_df.sample(n=top_k)
            for _, row in sample.iterrows():
                results.append({
                    'id': row['id'],
                    'title': row['name'],
                    'category': row['category'],
                    'level': row['level'],
                    'similarity': 0.3
                })

        return results