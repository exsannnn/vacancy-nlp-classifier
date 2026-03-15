import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
import pandas as pd
from scripts.utils.tech_extractor import extract_tech_list

csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

df = pd.read_csv(csv_path, sep=';', encoding='utf-8')

quality_scores = []
tech_stacks = []
scam_flags = []

for idx, row in df.iterrows():
    text = str(row['full_text']).lower()
    score = 5

    tech_words = ['python', 'pytorch', 'tensorflow', 'sql', 'docker', 'ml', 'aws', 'spark']
    tech_count = 0
    for word in tech_words:
        if word in text:
            tech_count += 1
    score += min(tech_count * 0.5, 2)

    bad_words = ['сетевой маркетинг', 'млм', 'вклад под', 'обучение за счет', 'работа на дому без опыта']
    for word in bad_words:
        if word in text:
            score -= 2

    good_words = ['удален', 'гибрид', 'официальное', 'дмс', 'страхование']
    for word in good_words:
        if word in text:
            score += 0.5

    if score > 10:
        score = 10
    if score < 1:
        score = 1

    quality_scores.append(int(score))

    found_tech = extract_tech_list(text)
    tech_stacks.append(','.join(found_tech))

    scam_count = 0
    if 'сетевой маркетинг' in text:
        scam_count += 1
    if 'млм' in text:
        scam_count += 1
    if 'вклад под' in text:
        scam_count += 1
    if 'обучение за счет' in text:
        scam_count += 1

    if scam_count >= 2:
        scam_flags.append('да')
    elif scam_count == 1:
        scam_flags.append('возможно')
    else:
        scam_flags.append('нет')

df['quality_score'] = quality_scores
df['tech_stack'] = tech_stacks
df['scam_flag'] = scam_flags

df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')

print(df['quality_score'].value_counts().sort_index())
print(df['tech_stack'].head())
print(df['scam_flag'].value_counts())