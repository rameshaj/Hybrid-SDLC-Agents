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
    try:
        # Get all running processes with the specified name
        result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if process_name in line:
                pid = int(line.split()[1])
                pids.append(pid)
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)  # Wait for 1 second before checking again
    except subprocess.CalledProcessError:
        pass
    return len(pids)