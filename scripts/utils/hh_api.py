import requests
import time

USER_AGENT = "ml-vacancy-scraper/0.1 (your@email.com)"
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0

def safe_request(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT, max_retries=MAX_RETRIES):
    if headers is None:
        headers = {"User-Agent": USER_AGENT}
    else:
        headers.setdefault("User-Agent", USER_AGENT)

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"429 Слишком много запросов, ожидание {wait:.1f}с (попытка {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса (попытка {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(RETRY_BACKOFF * (2 ** attempt))
    return None

def fetch_vacancy_details(vacancy_id):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = safe_request(url)
    return response.json() if response else None

def fetch_vacancies_search(params):
    url = "https://api.hh.ru/vacancies"
    response = safe_request(url, params=params)
    return response.json() if response else None