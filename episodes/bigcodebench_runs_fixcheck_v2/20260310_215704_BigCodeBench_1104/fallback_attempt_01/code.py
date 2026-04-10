import subprocess
import os
import threading

def task_func(script_path: str, timeout: int = 60) -> str:
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"{script_path} does not exist.")
    
    def target():
        subprocess.run(['python', script_path], check=True)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return "Terminating process due to timeout."
    else:
        return "Script executed successfully."