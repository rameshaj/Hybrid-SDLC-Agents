import subprocess
import os
import random

def task_func(directory, file_list):
    if not file_list:
        return None
    
    selected_file = random.choice(file_list)
    file_path = os.path.join(directory, selected_file)
    
    if not os.path.isfile(file_path):
        return None
    
    process = subprocess.Popen(file_path, shell=True)
    process.wait()
    return process.returncode