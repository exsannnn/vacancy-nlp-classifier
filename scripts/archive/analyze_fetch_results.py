from pathlib import Path
import pandas as pd
import config
import json

VAC_WITH_DESC = Path(config.PROJECT_ROOT) / "data" / "processed" / "vacancies_with_desc.csv"
CHECKPOINT = Path(config.PROJECT_ROOT) / "data" / "processed" / "desc_progress.json"

def load_checkpoint(cp_path):
    if not cp_path.exists():
        return {}
    return json.loads(cp_path.read_text(encoding="utf-8"))

def main():
    if not VAC_WITH_DESC.exists():
        print("Файл не найден:", VAC_WITH_DESC)
        return

    df = pd.read_csv(VAC_WITH_DESC, encoding="utf-8-sig")

    if "desc_fetched_at" in df.columns:
        df["desc_fetched_at"] = pd.to_datetime(df["desc_fetched_at"], utc=True, errors="coerce")
    else:
        df["desc_fetched_at"] = pd.NaT

    has_desc_text = df["description_text"].astype(str).str.strip() != ""
    has_desc_html = df["description_html"].astype(str).str.strip() != ""

    total = len(df)
    n_text = has_desc_text.sum()
    n_html = has_desc_html.sum()
    n_no_desc = total - n_text

    print(f"Всего строк: {total}")
    print(f"Вакансий с description_text (чистый текст): {n_text}")
    print(f"Вакансий с description_html (html): {n_html}")
    print(f"Вакансий без описания: {n_no_desc}")

    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df_with_desc = df[has_desc_text].copy()
    print("\nДиапазон дат (вакансии с описанием):", df_with_desc["published_at"].min(), "—", df_with_desc["published_at"].max())

    print("\nТоп городов (с описанием):")
    print(df_with_desc["area"].value_counts().head(20))

    checkpoint = load_checkpoint(CHECKPOINT)
    failed_ids = [vid for vid, status in checkpoint.items() if status != "ok"]
    print(f"\nВ checkpoint найдены {len(checkpoint)} id, из них failed/other: {len(failed_ids)}")

    failed_path = Path(config.PROJECT_ROOT) / "data" / "processed" / "failed_description_ids.txt"
    failed_path.write_text("\n".join(failed_ids), encoding="utf-8")
    print("Список failed id сохранён в", failed_path)

    sample_with_desc = df_with_desc.sample(n=min(200, len(df_with_desc)), random_state=42)
    sample_with_desc.to_csv(
        Path(config.PROJECT_ROOT) / "data" / "processed" / "with_desc_sample.csv",
        index=False, encoding="utf-8-sig"
    )
    print("Сохранён sample с описаниями: data/processed/with_desc_sample.csv")

    df_no_desc = df[~has_desc_text].copy()
    cols_keep = [c for c in ["id", "name", "snippet_requirement", "snippet_responsibility", "area", "employer", "published_at"] if c in df_no_desc.columns]
    df_no_desc[cols_keep].to_csv(
        Path(config.PROJECT_ROOT) / "data" / "processed" / "no_desc_list.csv",
        index=False, encoding="utf-8-sig"
    )
    print("Сохранён список вакансий без описания: data/processed/no_desc_list.csv")

    print(f"\nПроцент успешно скачанных описаний: {n_text / total * 100:.2f}%")

    print("\nРекомендация:")
    print("- Просмотреть data/processed/with_desc_sample.csv для оценки качества описаний (достаточно ли информации для разметки навыков).")
    print("- Если многие description пустые: можно использовать snippet (snippet_requirement + snippet_responsibility) как fallback при разметке.")
    print("- Файл failed_description_ids.txt можно держать под контролем и попробовать докачать позднее с увеличенным SLEEP или вручную проверить несколько id.")

    df.to_csv(VAC_WITH_DESC, index=False, encoding="utf-8-sig")
    print("\nПерезаписан файл с исправленным типом desc_fetched_at:", VAC_WITH_DESC)

if __name__ == "__main__":
    main()