gguf_init_from_file: failed to open GGUF file 'models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf'
gguf_init_from_file: failed to open GGUF file 'models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf'



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate([]) == []
    assert candidate([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert candidate([1, 2, 3, 2, 4, 3, 5]) == [1, 4, 5]


def __run_tests():
    check(globals().get('remove_duplicates'))

if __name__ == '__main__':
    __run_tests()
