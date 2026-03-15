import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')