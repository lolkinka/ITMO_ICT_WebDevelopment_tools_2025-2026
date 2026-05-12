import time
from multiprocess_parser import run_multiprocessing
from threading_parser import run_threading
from async_parser import run_async
from settings import ARTICLE_IDS
import asyncio

if __name__ == '__main__':
    print("Запуск Threading ===")
    start_time = time.time()
    run_threading(ARTICLE_IDS)
    print(f"Threading занял: {time.time() - start_time:.4f} сек\n")

    print("Запуск Multiprocessing ===")
    start_time = time.time()
    run_multiprocessing(ARTICLE_IDS)
    print(f"Multiprocessing занял: {time.time() - start_time:.4f} сек\n")

    print("Запуск Async ===")
    start_time = time.time()
    asyncio.run(run_async(ARTICLE_IDS))
    print(f"Async занял: {time.time() - start_time:.4f} сек\n")