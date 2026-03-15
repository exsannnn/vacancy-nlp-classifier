import config
import os

csv_path = os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv')

with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(csv_path, 'w', encoding='utf-8-sig') as f:
    for line in lines:
        f.write(line)

print("Файл перекодирован в UTF-8.")