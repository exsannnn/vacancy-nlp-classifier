import pytest
import pickle
import os
import config
from backend.ranker import RankerService
from backend.recommend import RecommenderService

def test_ranker_service():
    ranker = RankerService()
    score = ranker.predict_quality("Python разработчик, Django, SQL")
    assert 1 <= score <= 10
    assert isinstance(score, int)

def test_recommender_service():
    recommender = RecommenderService()
    recommendations = recommender.recommend("Python", top_k=3)
    assert isinstance(recommendations, list)
    if recommendations:
        assert 'id' in recommendations[0]
        assert 'title' in recommendations[0]

def test_vectorizer_loading():
    vectorizer_path = os.path.join(config.PROJECT_ROOT, 'models', 'basic', 'vectorizer.pkl')
    assert os.path.exists(vectorizer_path)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    assert hasattr(vectorizer, 'transform')

def test_category_model_loading():
    model_path = os.path.join(config.PROJECT_ROOT, 'models', 'basic', 'cat_model.pkl')
    assert os.path.exists(model_path)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    assert hasattr(model, 'predict')