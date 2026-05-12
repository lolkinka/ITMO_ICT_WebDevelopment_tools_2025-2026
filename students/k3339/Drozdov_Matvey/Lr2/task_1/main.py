import time
import asyncio
from multiprocessing_sum import run_multiprocessing
from threading_sum import run_threading
from async_sum import run_async

TARGET_NUMBER = 100_000_000

NUM_TASKS = 4

if __name__ == '__main__':
    print(f"Вычисление суммы от 1 до {TARGET_NUMBER:,}\n")

    start_time = time.time()
    result_mp = run_multiprocessing(TARGET_NUMBER, NUM_TASKS)
    mp_time = time.time() - start_time
    print(f"Multiprocessing:")
    print(f"Результат: {result_mp} | Время: {mp_time:.4f} сек\n")

    start_time = time.time()
    result_th = run_threading(TARGET_NUMBER, NUM_TASKS)
    th_time = time.time() - start_time
    print(f"Threading:")
    print(f"Результат: {result_th} | Время: {th_time:.4f} сек\n")

    start_time = time.time()
    result_as = asyncio.run(run_async(TARGET_NUMBER, NUM_TASKS))
    as_time = time.time() - start_time
    print(f"Asyncio:")
    print(f"Результат: {result_as} | Время: {as_time:.4f} сек\n")