#!/bin/bash
export PYTHONPATH=/app:$PYTHONPATH

python scripts/data_collection/update_data.py
python scripts/data_collection/check_vacancy_status.py
python scripts/utils/create_quality_scores.py
python scripts/training/train_ner_model.py
python scripts/preprocessing/preprocess.py
python scripts/training/train_basic_model.py
python scripts/training/create_embeddings.py
exec python -m backend.app