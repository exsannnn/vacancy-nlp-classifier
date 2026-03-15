import pandas as pd
import config
import os

PATH = os.path.join(config.PROJECT_ROOT, "data", "processed", "vacancies.csv")
df = pd.read_csv(PATH, encoding="utf-8-sig")

print("Строк:", len(df))
print("\nКолонки:")
print(df.columns.tolist())

print("\nПервые 5 строк:")
cols = ["id", "name", "area", "published_at", "employer", "experience"]
print(df[cols].head())

print("\nПропущенные значения по колонкам:")
print(df.isna().sum())

df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
print("\nДиапазон дат:", df["published_at"].min(), "—", df["published_at"].max())

print("\nТоп городов:")
print(df["area"].value_counts().head(20))

print("\nСтатистика по опыту работы:")
if 'experience' in df.columns:
    exp_counts = df['experience'].value_counts()
    for exp, count in exp_counts.items():
        print(f"{exp}: {count} ({count/len(df)*100:.1f}%)")

if 'salary_from' in df.columns or 'salary_to' in df.columns:
    print("\nЗарплатные данные:")
    if 'salary_from' in df.columns:
        print(f"Вакансий с указанием зарплаты 'от': {df['salary_from'].notna().sum()}")
    if 'salary_to' in df.columns:
        print(f"Вакансий с указанием зарплаты 'до': {df['salary_to'].notna().sum()}")
else:
    print("\nЗарплатные данные отсутствуют")

sample_path = os.path.join(config.PROJECT_ROOT, "data", "processed", "sample_for_manual_check.csv")
df.sample(20, random_state=42).to_csv(sample_path, index=False, encoding="utf-8-sig")
print("\nСохранен sample_for_manual_check.csv (20 строк) для быстрой ручной проверки.")