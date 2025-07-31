import time

class TimeSpanLogger:
    def __init__(self):
        self._start_time = None
        self._end_time = None

    def start(self):
        self._start_time = time.perf_counter()
        self._end_time = None

    def stop(self):
        if self._start_time is None:
            raise RuntimeError("start() must be called before stop()")
        self._end_time = time.perf_counter()

    def elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        if self._end_time is None:
            return time.perf_counter() - self._start_time
        return self._end_time - self._start_time

    def __str__(self):
        return f"{self.elapsed():.4f} seconds"


# when have time will merge with logging (not necessary to seperate timer and logging in this project)