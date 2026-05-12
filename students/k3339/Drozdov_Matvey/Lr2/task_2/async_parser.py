import aiohttp
from settings import hash_password, HEADERS
import asyncio
import random
import asyncpg

DSN = "postgresql://postgres:postgres@localhost:5432/finance_db"
semaphore = asyncio.Semaphore(5)

async def save_to_db_async(pool, name, login, hashed_password):
    async with pool.acquire() as conn:
        query = """
            INSERT INTO "user" (name, login, hashed_password)
            VALUES ($1, $2, $3);
        """
        await conn.execute(query, name, login, hashed_password)

async def parse_and_save_async(target_id, session, pool):
    url = f"https://stopgame.ru/ajax/comments/get?target_id={target_id}&target_type=news"

    async with semaphore:
        try:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                data = await response.json()

                saved_count = 0
                seen_names = set()

                for comment in data.get('comments', []):
                    raw_name = comment.get('userInfo', {}).get('user_name')

                    if raw_name and raw_name not in seen_names:
                        seen_names.add(raw_name)

                        name = raw_name[:50]
                        login = f"{raw_name.lower()}_{random.randint(1000, 9999)}"
                        hashed_pwd = hash_password("student2026")

                        await save_to_db_async(pool, name, login, hashed_pwd)
                        print(f"Сохранен: {login} (из новости {target_id})")

                        saved_count += 1
                        if saved_count >= 10:
                            break

        except Exception as e:
            print(f"Не удалось получить данные по ID {target_id}: {e}")

async def run_async(article_ids):
    pool = await asyncpg.create_pool(dsn=DSN, min_size=5, max_size=10)

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [parse_and_save_async(target_id, session, pool) for target_id in article_ids]
        await asyncio.gather(*tasks)
    await pool.close()