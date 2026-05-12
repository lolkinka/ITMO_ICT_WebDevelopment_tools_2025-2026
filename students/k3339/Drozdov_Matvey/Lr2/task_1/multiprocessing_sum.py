import multiprocessing

def get_ranges(target, num_tasks):
    chunk_size = target // num_tasks
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else target
        ranges.append((start, end))
    return ranges

def calculate_sum(start, end):
    return sum(range(start, end + 1))

def run_multiprocessing(target, chunks):
    ranges = get_ranges(target, chunks)
    with multiprocessing.Pool(processes=chunks) as pool:
        results = pool.starmap(calculate_sum, ranges)
    return sum(results)