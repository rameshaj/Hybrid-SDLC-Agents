import subprocess
import os
import threading

def task_func(script_path: str, timeout: int = 60) -> str:
    """
    Execute a specified python code with a given timeout. If the script execution exceeds the timeout, it is terminated.

    Parameters:
    - script_path (str): The path to the Python code to be executed.
    - timeout (int): The maximum allowed time (in seconds) for the script execution. Default is 60 seconds.

    Returns:
    - str: A message indicating if the code was terminated due to timeout or executed successfully. The message is either "Script executed successfully." or "Terminating process due to timeout."

    Requirements:
    - subprocess
    - os
    - threading

    Examples:
    >>> task_func('/pathto/MyrScript.py')
    'Script executed successfully.'
    
    >>> task_func('/pathto/LongRunningScript.py', 30)
    'Terminating process due to timeout.'

    Note:
    - If the script was terminated due to timeout it will return "Script executed successfully.", otherwise "Terminating process due to timeout."

    Raise:
    - The code will raise FileNotFoundError if the file is not exist.
    """
    try:
        # Start the subprocess
        process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Create a thread to check the process status
        def check_process():
            nonlocal process
            if process.poll() is not None:
                raise subprocess.TimeoutExpired(f"Script execution timed out after {timeout} seconds.")
        
        thread = threading.Thread(target=check_process)
        thread.start()
        
        # Wait for the script to finish or the timeout to occur
        try:
            output, error = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            thread.join()
            raise e
        
        # Check if the process was terminated due to timeout
        if process.poll() is not None:
            return "Terminating process due to timeout."
        
        return "Script executed successfully."
    except FileNotFoundError:
        return "File not found."