import subprocess
import os
import signal
import time

def task_func(process_name: str) -> int:
    pids = subprocess.check_output(["pgrep", process_name]).decode().strip().split()
    count = 0
    for pid in pids:
        os.kill(int(pid), signal.SIGTERM)
        count += 1
    time.sleep(1)
    return count