def file_name_check(file_name):
    import re

    # Check if the file name contains more than three digits
    if len(re.findall(r'\d', file_name)) > 3:
        return 'No'

    # Check if there is exactly one dot in the file name
    if file_name.count('.') != 1:
        return 'No'

    # Split the file name into parts before and after the dot
    parts = file_name.split('.')
    before_dot, after_dot = parts[0], parts[1]

    # Check if the substring before the dot is not empty and starts with a letter
    if not before_dot or not before_dot[0].isalpha():
        return 'No'

    # Check if the substring after the dot is one of ['txt', 'exe', 'dll']
    if after_dot not in ['txt', 'exe', 'dll']:
        return 'No'

    return 'Yes'