LOGFILE_PATH = "logfile.log"

import subprocess
import time
import json
import platform

def task_func(interval, duration):
    if interval <= 0 or duration <= 0:
        raise ValueError("Both interval and duration must be greater than zero.")
    
    cpu_usage_data = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if platform.system() == "Windows":
            cpu_usage = subprocess.check_output("wmic cpu get loadpercentage", shell=True)
            cpu_usage = int(cpu_usage.decode().split('\n')[1].strip())
        else:
            cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)'", shell=True)
            cpu_usage = 100 - float(cpu_usage.decode().split(',')[3].split()[0])
        
        timestamp = time.time()
        cpu_usage_data.append({"timestamp": timestamp, "cpu_usage": cpu_usage})
        
        time.sleep(interval)
    
    try:
        with open(LOGFILE_PATH, 'w') as logfile:
            json.dump(cpu_usage_data, logfile)
    except IOError:
        return None
    
    return LOGFILE_PATH