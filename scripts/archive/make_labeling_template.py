from pathlib import Path
import pandas as pd
import config

INPUT = Path(config.PROJECT_ROOT) / "data" / "processed" / "vacancies_with_desc.csv"
OUT = Path(config.PROJECT_ROOT) / "data" / "processed" / "labeling_template.csv"
SAMPLE_OUT = Path(config.PROJECT_ROOT) / "data" / "processed" / "manual_labeling_sample.csv"
SAMPLE_SIZE = 120
MAX_CHARS = 2000
RANDOM_STATE = 42

CATEGORIES = ["ml", "data", "backend", "research", "cv", "nlp", "unknown"]
LEVELS = ["junior", "middle", "senior", "unknown"]

def make_full_text(name, desc, max_chars):
    name = "" if pd.isna(name) else str(name)
    desc = "" if pd.isna(desc) else str(desc)
    name = name.strip()
    desc = desc.strip()
    full = (name + ". " + desc).strip()
    full = full.replace("\r", " ").replace("\n", " ")
    if len(full) > max_chars:
        snippet = full[:max_chars]
        last_space = snippet.rfind(" ")
        if last_space > int(max_chars * 0.6):
            snippet = snippet[:last_space]
        full = snippet + " ..."
    return full

def main():
    if not INPUT.exists():
        print("Входной файл не найден:", INPUT)
        return

    df = pd.read_csv(INPUT, encoding="utf-8-sig")

    if "description_text" in df.columns:
        desc_col = "description_text"
    elif "description_html" in df.columns:
        desc_col = "description_html"
    else:
        n = len(df)
        req = df["snippet_requirement"].fillna("") if "snippet_requirement" in df.columns else pd.Series([""] * n)
        resp = df["snippet_responsibility"].fillna("") if "snippet_responsibility" in df.columns else pd.Series([""] * n)
        df["__snippet"] = (req + " " + resp).str.strip()
        desc_col = "__snippet"

    df["full_text"] = df.apply(lambda r: make_full_text(r.get("name", ""), r.get(desc_col, ""), MAX_CHARS), axis=1)

    top_cities = df["area"].value_counts().head(6).index.tolist()
    sampled = []
    per_city = max(3, int(SAMPLE_SIZE * 0.6 / max(1, len(top_cities)))) if top_cities else 0
    for city in top_cities:
        chunk = df[df["area"] == city]
        n = min(per_city, len(chunk))
        if n > 0:
            sampled.append(chunk.sample(n=n, random_state=RANDOM_STATE))

    already = pd.concat(sampled).index if sampled else []
    remaining = df[~df.index.isin(already)].sample(n=max(0, SAMPLE_SIZE - sum(len(x) for x in sampled)), random_state=RANDOM_STATE)
    if sampled:
        sampled.append(remaining)
        sample_df = pd.concat(sampled).reset_index(drop=True)
    else:
        sample_df = remaining.reset_index(drop=True)

    out = sample_df[["id", "name", "full_text"]].copy()
    out["category"] = ""
    out["level"] = ""
    out["skills"] = ""
    out["notes"] = ""

    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    sample_df.to_csv(SAMPLE_OUT, index=False, encoding="utf-8-sig")

    readme = OUT.with_suffix(".readme.txt")
    readme.write_text(
        "Инструкция для разметки (labeling_template.csv):\n\n"
        "Колонки:\n"
        " - id: уникальный id вакансии (не менять)\n"
        " - name: заголовок вакансии (инфо для контекста)\n"
        " - full_text: объединённый текст (title + description), используйте для принятия решения\n"
        " - category: выберите одну из: " + ", ".join(CATEGORIES) + "\n"
        " - level: выберите одну из: " + ", ".join(LEVELS) + "\n"
        " - skills: перечислите навыки через запятую, lowercase, без пробелов вокруг запятой\n"
        "   Пример: python,pytorch,sql\n"
        " - notes: любые дополнительные замечания\n\n"
        "Рекомендации по разметке:\n"
        " - category: по сути работы (что требуется делать), а не по стеку\n"
        " - level: ориентируйтесь на требования в тексте (опыт, senior/lead в тексте -> senior)\n"
        " - skills: перечисляйте только явные упоминания или очевидные следствия\n"
        " - если не уверены — ставьте 'unknown' в category/level\n\n"
        "Как разметить: откройте labeling_template.csv в Excel или Google Sheets и заполните колонки category, level, skills, notes.\n",
        encoding="utf-8"
    )

    print("Шаблон создан:", OUT)
    print("Сохранён sample (полный контекст):", SAMPLE_OUT)
    print("Инструкция рядом:", readme)
    print("Размер шаблона:", len(out), "строк.")

if __name__ == "__main__":
    main()