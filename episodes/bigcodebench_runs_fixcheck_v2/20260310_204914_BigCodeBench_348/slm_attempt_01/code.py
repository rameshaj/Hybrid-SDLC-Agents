import subprocess
import os
import signal
import time

def task_func(process_name: str) -> int:
    """
    Stops all running processes with a specific name.

    Parameters:
    process_name (str): The name of the processes to be stopped.

    Returns:
    int: The number of processes stopped. If no processes are found, returns 0.

    Requirements:
    - subprocess
    - os
    - signal
    - time

    Note:
    - The function sends a termination signal to the processes and waits for 1 second. 
      There is no guarantee that all processes will have terminated within this time.

    Example:
    >>> pids = task_func('test_name') # Dummy example, should return 0
    >>> pids
    0
    """
    pids = []
    for proc in subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE).communicate()[0].decode().split('\n'):
        if process_name in proc:
            pid = int(proc.split()[1])
            pids.append(pid)
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)  # Wait for 1 second
            except ProcessLookupError:
                pass

    return len(pids)