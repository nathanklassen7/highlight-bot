import os
import time


def wait_for_files_written(paths, attempts=10, interval=0.5):
    for _ in range(attempts):
        time.sleep(interval)
        if all(os.path.exists(p) and os.path.getsize(p) > 0 for p in paths):
            return True
    return False
