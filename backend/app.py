from flask import Flask, request, jsonify, render_template, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scripts.utils import RankerService
from scripts.utils import RecommenderService
import pandas as pd
import config
import pickle
import re
import os
import requests
import time
import subprocess
import sys

app = Flask(__name__)

models_dir = os.path.join(config.PROJECT_ROOT, 'models', 'basic')
csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

vectorizer = pickle.load(open(os.path.join(models_dir, 'vectorizer.pkl'), 'rb'))
cat_model = pickle.load(open(os.path.join(models_dir, 'cat_model.pkl'), 'rb'))
lvl_model = pickle.load(open(os.path.join(models_dir, 'lvl_model.pkl'), 'rb'))
le_category = pickle.load(open(os.path.join(models_dir, 'le_category.pkl'), 'rb'))
le_level = pickle.load(open(os.path.join(models_dir, 'le_level.pkl'), 'rb'))

ranker = RankerService()
recommender = RecommenderService()

def run_update_pipeline():
    with app.app_context():
        print("Запуск автоматического обновления данных и моделей...")
        scripts = [
            "scripts/data_collection/update_data.py",
            "scripts/data_collection/check_vacancy_status.py",
            "scripts/utils/create_quality_scores.py",
            "scripts/training/train_ner_model.py",
            "scripts/preprocessing/preprocess.py",
            "scripts/training/train_basic_model.py",
            "scripts/training/create_embeddings.py"
        ]
        for script in scripts:
            script_path = os.path.join(config.PROJECT_ROOT, script)
            print(f"  → {script}")
            try:
                result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Ошибка в {script}: {e.stderr}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=run_update_pipeline, trigger=CronTrigger(hour=3, minute=0))
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.form.get('text', '')
    cleaned = text.lower()
    cleaned = re.sub(r'[^а-яёa-z0-9\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    vectorized = vectorizer.transform([cleaned])
    cat_pred = cat_model.predict(vectorized)[0]
    lvl_pred = lvl_model.predict(vectorized)[0]
    cat_name = le_category.inverse_transform([cat_pred])[0]
    lvl_name = le_level.inverse_transform([lvl_pred])[0]
    quality_score = ranker.predict_quality(text)
    recommendations = recommender.recommend(text, 5)

    tech_keywords = {
        'python': ['python', 'питон'],
        'django': ['django'],
        'flask': ['flask'],
        'docker': ['docker', 'контейнер'],
        'kubernetes': ['kubernetes', 'k8s'],
        'sql': ['sql', 'postgresql', 'mysql'],
        'pytorch': ['pytorch', 'torch'],
        'tensorflow': ['tensorflow', 'tf'],
        'aws': ['aws', 'amazon'],
        'gcp': ['gcp', 'google cloud'],
        'azure': ['azure'],
        'git': ['git'],
        'linux': ['linux'],
        'ml': ['ml', 'machine learning'],
        'ai': ['ai', 'artificial intelligence'],
        'nlp': ['nlp', 'natural language'],
        'cv': ['cv', 'computer vision']
    }
    found = []
    text_lower = str(text).lower()
    for tech, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found.append(tech)
                break
    tech_stack = list(set(found))

    scam_words = ['сетевой маркетинг', 'млм', 'вклад под', 'обучение за счет']
    scam_flag = 'нет'
    for word in scam_words:
        if word in text_lower:
            scam_flag = 'да' if scam_flag == 'да' else 'возможно'

    result = {
        'category': str(cat_name),
        'level': str(lvl_name),
        'quality_score': int(quality_score),
        'tech_stack': tech_stack,
        'scam_flag': scam_flag,
        'recommendations': []
    }

    for rec in recommendations:
        result['recommendations'].append({
            'id': int(rec['id']),
            'title': str(rec['title']),
            'category': str(rec['category']),
            'level': str(rec['level']),
            'similarity': float(rec['similarity'])
        })

    return jsonify(result)

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    if 'status' not in df.columns:
        df['status'] = 'active'
    results = []
    for _, row in df.iterrows():
        if row['status'] != 'active':
            continue
        if category and row['category'] != category:
            continue
        if level and row['level'] != level:
            continue
        if query and query.lower() not in str(row['full_text']).lower() and query.lower() not in str(row['name']).lower():
            continue
        tech_stack = []
        if 'tech_stack' in row:
            tech_stack = str(row['tech_stack']).split(',')
        results.append({
            'id': row['id'],
            'title': row['name'],
            'category': str(row['category']) if not pd.isna(row['category']) else 'unknown',
            'level': str(row['level']) if not pd.isna(row['level']) else 'unknown',
            'quality_score': int(row['quality_score']) if not pd.isna(row['quality_score']) else 5,
            'tech_stack': ','.join(tech_stack) if tech_stack else '',
            'status': row['status']
        })
    return jsonify({'results': results[:20]})

@app.route('/api/recommended', methods=['GET'])
def api_recommended():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    if 'status' not in df.columns:
        df['status'] = 'active'
    active_df = df[df['status'] == 'active']
    if len(active_df) > 8:
        active_df = active_df.sample(8)
    results = []
    for _, row in active_df.iterrows():
        results.append({
            'id': row['id'],
            'title': row['name'],
            'category': str(row['category']) if not pd.isna(row['category']) else 'unknown',
            'level': str(row['level']) if not pd.isna(row['level']) else 'unknown',
            'quality_score': int(row.get('quality_score', 5)) if not pd.isna(row.get('quality_score')) else 5,
            'tech_stack': str(row.get('tech_stack', ''))
        })
    return jsonify(results)

@app.route('/api/stats', methods=['GET'])
def api_stats():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    total = len(df)
    if 'status' not in df.columns:
        active = total
    else:
        active = len(df[df['status'] == 'active'])
    if 'quality_score' in df.columns:
        avg_quality = df['quality_score'].mean()
    else:
        avg_quality = 5
    return jsonify({'total': total, 'active': active, 'avgQuality': float(avg_quality)})

@app.route('/api/check_archive', methods=['POST'])
def api_check_archive():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    if 'status' not in df.columns:
        df['status'] = 'active'
    total_checked = 0
    archived_found = 0
    for index, row in df.iterrows():
        if total_checked >= 100:
            break
        if row['status'] == 'archived':
            continue
        vacancy_id = str(row['id'])
        url = f'https://api.hh.ru/vacancies/{vacancy_id}'
        headers = {'User-Agent': 'hh-vacancy-checker/1.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                df.at[index, 'status'] = 'archived'
                archived_found += 1
            elif response.status_code == 200:
                data = response.json()
                if data.get('archived') == True:
                    df.at[index, 'status'] = 'archived'
                    archived_found += 1
                else:
                    df.at[index, 'status'] = 'active'
            elif response.status_code == 403:
                break
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при проверке вакансии {vacancy_id}: {e}")
        total_checked += 1
        time.sleep(0.1)
    df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    print(f"Проверено вакансий: {total_checked}, архивных найдено: {archived_found}")
    return jsonify({'total_checked': total_checked, 'archived_found': archived_found})

@app.route('/api/vacancy/<int:vacancy_id>', methods=['GET'])
def api_vacancy_detail(vacancy_id):
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    vacancy = df[df['id'] == vacancy_id]
    if vacancy.empty:
        return jsonify({'error': 'Вакансия не найдена'}), 404
    row = vacancy.iloc[0]
    result = {
        'id': int(row['id']),
        'title': str(row['name']),
        'category': str(row['category']) if not pd.isna(row['category']) else 'unknown',
        'level': str(row['level']) if not pd.isna(row['level']) else 'unknown',
        'quality_score': int(row.get('quality_score', 5)) if not pd.isna(row.get('quality_score')) else 5,
        'tech_stack': str(row.get('tech_stack', '')),
        'full_text': str(row.get('full_text', '')),
        'status': str(row.get('status', 'active')),
        'published_at': str(row.get('published_at', ''))
    }
    return jsonify(result)

@app.route('/api/categories', methods=['GET'])
def api_categories():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    categories = df['category'].unique().tolist()
    return jsonify({'categories': categories})

@app.route('/api/levels', methods=['GET'])
def api_levels():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    levels = df['level'].unique().tolist()
    return jsonify({'levels': levels})

@app.route('/api/update_quality', methods=['POST'])
def api_update_quality():
    data = request.json
    vacancy_id = data.get('id')
    quality_score = data.get('quality_score')
    if not vacancy_id or quality_score is None:
        return jsonify({'error': 'Не указаны id или quality_score'}), 400
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    if vacancy_id not in df['id'].values:
        return jsonify({'error': 'Вакансия не найдена'}), 404
    df.loc[df['id'] == vacancy_id, 'quality_score'] = quality_score
    df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    return jsonify({'message': 'Качество обновлено', 'id': vacancy_id, 'quality_score': quality_score})

@app.route('/api/bulk_update_status', methods=['POST'])
def api_bulk_update_status():
    data = request.json
    ids = data.get('ids', [])
    status = data.get('status')
    if not ids or not status:
        return jsonify({'error': 'Не указаны ids или status'}), 400
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    updated_count = 0
    for vacancy_id in ids:
        if vacancy_id in df['id'].values:
            df.loc[df['id'] == vacancy_id, 'status'] = status
            updated_count += 1
    df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    return jsonify({'message': f'Статус обновлен для {updated_count} вакансий', 'updated': updated_count})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)