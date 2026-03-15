from scripts.utils.hh_api import fetch_vacancy_details
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import time
import json
import html
import re

INPUT_CSV = Path("data/processed/vacancies.csv")
OUTPUT_CSV = Path("data/processed/vacancies_with_desc.csv")
CHECKPOINT_JSON = Path("data/processed/desc_progress.json")
SLEEP_BETWEEN = 0.2
SAVE_EVERY = 50

def strip_html_tags(html_text):
    if not isinstance(html_text, str):
        return ""
    text = re.sub(r"<script.*?>.*?</script>", " ", html_text, flags=re.S|re.I)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.S|re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_checkpoint():
    if CHECKPOINT_JSON.exists():
        return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))
    return {}

def save_checkpoint(d):
    CHECKPOINT_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    if OUTPUT_CSV.exists():
        df_out = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig")
        df = df.merge(df_out[["id", "description_html", "description_text", "desc_fetched_at"]], on="id", how="left")
    else:
        df["description_html"] = ""
        df["description_text"] = ""
        df["desc_fetched_at"] = pd.NaT
    checkpoint = load_checkpoint()
    ids = df["id"].astype(str).tolist()
    to_process = [vid for vid in ids if not df.loc[df["id"].astype(str) == vid, "description_html"].astype(bool).any()]
    print(f"Всего строк: {len(df)}, нужно загрузить описания для: {len(to_process)}")
    processed_count = 0
    for i, vid in enumerate(to_process, start=1):
        if vid in checkpoint and checkpoint[vid] == "ok":
            continue
        js = fetch_vacancy_details(vid)
        if js is None:
            checkpoint[vid] = "failed"
            save_checkpoint(checkpoint)
            continue
        desc_html = js.get("description") or ""
        desc_txt = strip_html_tags(desc_html)
        ts = datetime.now(timezone.utc).isoformat()
        mask = df["id"].astype(str) == vid
        df.loc[mask, "description_html"] = desc_html
        df.loc[mask, "description_text"] = desc_txt
        df.loc[mask, "desc_fetched_at"] = ts
        checkpoint[vid] = "ok"
        processed_count += 1
        if processed_count % SAVE_EVERY == 0:
            df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
            save_checkpoint(checkpoint)
            print(f"Сохранён прогресс: загружено {processed_count} описаний")
        time.sleep(SLEEP_BETWEEN)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    save_checkpoint(checkpoint)
    print("Готово. Сохранено в", OUTPUT_CSV)

if __name__ == "__main__":
    main()