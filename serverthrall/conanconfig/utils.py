from chardet.universaldetector import UniversalDetector


def guess_file_encoding(path):
    detector = UniversalDetector()

    with open(path, 'rb') as file:
        for line in file:
            detector.feed(line)
            if detector.done:
                break

    detector.close()
    guessed = detector.result

    use_guess = (
        guessed['encoding'] is not None and
        guessed['encoding'] != 'ascii' and
        guessed['confidence'] >= 1)

    if use_guess:
        return guessed['encoding']

    return 'utf-8'
