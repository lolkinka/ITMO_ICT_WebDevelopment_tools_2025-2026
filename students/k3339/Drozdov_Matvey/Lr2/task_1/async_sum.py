import asyncio

def get_ranges(target, num_tasks):
    chunk_size = target // num_tasks
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else target
        ranges.append((start, end))
    return ranges

async def calculate_sum_async(start, end):
    return sum(range(start, end + 1))

async def run_async(target, chunks):
    ranges = get_ranges(target, chunks)
    tasks = [calculate_sum_async(start, end) for start, end in ranges]
    results = await asyncio.gather(*tasks)
    return sum(results)