import multiprocessing
import requests
from settings import save_to_db,HEADERS, hash_password
import random

def parse_and_save_sync(target_id):
    url = f"https://stopgame.ru/ajax/comments/get?target_id={target_id}&target_type=news"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()

        saved_count = 0
        seen_names = set()

        for comment in data.get('comments', []):
            raw_name = comment.get('userInfo', {}).get('user_name')

            if raw_name and raw_name not in seen_names:
                seen_names.add(raw_name)

                name = raw_name[:50]
                login = f"{raw_name.lower()}_{random.randint(1000, 9999)}"
                hashed_pwd = hash_password("student2026")

                save_to_db(name, login, hashed_pwd)
                print(f"Сохранен: {login} (из новости {target_id})")

                saved_count += 1
                if saved_count >= 10:
                    break

    except Exception as e:
        print(f"Не удалось получить данные по ID {target_id}: {e}")


def run_multiprocessing(article_ids):
    with multiprocessing.Pool(processes=len(article_ids)) as pool:
        pool.map(parse_and_save_sync, article_ids)