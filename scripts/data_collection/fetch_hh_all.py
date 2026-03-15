from scripts.utils.hh_api import fetch_vacancies_search, fetch_vacancy_details
from datetime import datetime, timezone
from urllib.parse import quote_plus
from time import sleep
import pandas as pd
import json
import os

SEARCH_QUERIES = [
    "machine learning",
    "ml",
    "data scientist",
    "data science",
    "python developer",
    "ai"
]
AREA_RUSSIA = 113
PER_PAGE = 20
MAX_PAGES_PER_QUERY = 50
OUTPUT_RAW_DIR = "data/raw"
OUTPUT_PROCESSED = "data/processed/vacancies.csv"
SLEEP_BETWEEN_REQUESTS = 0.3
FETCH_FULL_VACANCY = False

def ensure_dirs():
    os.makedirs(OUTPUT_RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PROCESSED), exist_ok=True)

def slugify(q):
    return quote_plus(q.replace(" ", "_"))

def save_raw(query_slug, page, data):
    fname = os.path.join(OUTPUT_RAW_DIR, f"{query_slug}_page_{page}.json")
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_simple_from_item(item):
    salary = item.get("salary") or {}
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "area": (item.get("area") or {}).get("name"),
        "published_at": item.get("published_at"),
        "employer": (item.get("employer") or {}).get("name"),
        "experience": (item.get("experience") or {}).get("name"),
        "schedule": (item.get("schedule") or {}).get("name"),
        "salary_from": salary.get("from"),
        "salary_to": salary.get("to"),
        "salary_currency": salary.get("currency"),
        "snippet_requirement": (item.get("snippet") or {}).get("requirement"),
        "snippet_responsibility": (item.get("snippet") or {}).get("responsibility"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_item": item
    }

def main():
    ensure_dirs()
    all_rows = []
    seen_ids = set()
    for q in SEARCH_QUERIES:
        print("Запрос:", q)
        q_slug = slugify(q)
        page = 0
        pages_done = 0
        while pages_done < MAX_PAGES_PER_QUERY:
            params = {
                "text": q,
                "area": AREA_RUSSIA,
                "per_page": PER_PAGE,
                "page": page
            }
            data = fetch_vacancies_search(params)
            if data is None:
                print(f"Не удалось загрузить страницу {page} для запроса {q}")
                break
            items = data.get("items", [])
            if not items:
                print(f"Пустая страница {page} для запроса {q}")
                break
            save_raw(q_slug, page, data)
            print(f"Запрос '{q}' страница {page}: получено {len(items)} вакансий")
            for item in items:
                vid = item.get("id")
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)
                row = extract_simple_from_item(item)
                if FETCH_FULL_VACANCY:
                    full = fetch_vacancy_details(vid)
                    if full:
                        row["description"] = full.get("description")
                        row["vacancy_full_raw"] = full
                all_rows.append(row)
            page += 1
            pages_done += 1
            sleep(SLEEP_BETWEEN_REQUESTS)
    if not all_rows:
        print("Не собрано ни одной вакансии.")
        return
    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset="id").reset_index(drop=True)
    print("Всего уникальных вакансий:", len(df))
    df.to_csv(OUTPUT_PROCESSED, index=False, encoding="utf-8-sig")
    print("Обработанные данные сохранены в:", OUTPUT_PROCESSED)

if __name__ == "__main__":
    main()