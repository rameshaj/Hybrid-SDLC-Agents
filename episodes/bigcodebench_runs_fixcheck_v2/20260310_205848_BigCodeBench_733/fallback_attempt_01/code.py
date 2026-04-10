import re
import string

def task_func(content):
    stop_words = set(['a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'theirs', 'he', 'him', 'his', 'she', 'her', 'hers', 'we', 'us', 'our', 'ours', 'you', 'your', 'yours'])
    words = re.findall(r'\b\w+\b', content.lower())
    if len(words) > 1:
        words = words[:-1]
    return sum(1 for word in words if word not in stop_words)