def is_bored(S):
    sentences = S.split('.')
    sentences += S.split('?')
    sentences += S.split('!')
    bored_count = 0
    for sentence in sentences:
        if sentence.strip().startswith('I'):
            bored_count += 1
    return bored_count