import threading

def get_ranges(target, num_tasks):
    chunk_size = target // num_tasks
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else target
        ranges.append((start, end))
    return ranges

def calculate_and_store(start, end, results_list, index):
    results_list[index] = sum(range(start, end + 1))


def run_threading(target, chunks):
    ranges = get_ranges(target, chunks)
    threads = []

    results = [0] * chunks

    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=calculate_and_store,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    return sum(results)