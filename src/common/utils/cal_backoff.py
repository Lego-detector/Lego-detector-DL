def cal_backoff(attempt: int, min_time: int = 0, max_time: int = 60):
    return min(min_time + 2 ** attempt, max_time)