import matplotlib.pyplot as plt
import pandas as pd
import config
import os

df = pd.read_csv(
    os.path.join(config.PROJECT_ROOT, 'data', 'processed', 'labeled_vacancies.csv'),
    sep=';', encoding='utf-8'
)

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

cat_counts = df['category'].value_counts()
axes[0].bar(cat_counts.index, cat_counts.values)
axes[0].set_title('Распределение категорий')
axes[0].tick_params(axis='x', rotation=45)

lvl_counts = df['level'].value_counts()
axes[1].bar(lvl_counts.index, lvl_counts.values)
axes[1].set_title('Распределение уровней')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(config.PROJECT_ROOT, 'data_analysis.png'), dpi=300)

print("Статистика по данным:")
print(f"Всего записей: {len(df)}")
print(f"\nКоличество категорий: {len(cat_counts)}")
print(f"Количество уровней: {len(lvl_counts)}")
print(f"\nСредняя длина текста: {df['full_text'].str.len().mean():.0f} символов")

print("\nДисбаланс классов (категории):")
for cat, count in cat_counts.items():
    print(f"{cat}: {count} ({count/len(df)*100:.1f}%)")

print("\nДисбаланс классов (уровни):")
for lvl, count in lvl_counts.items():
    print(f"{lvl}: {count} ({count/len(df)*100:.1f}%)")