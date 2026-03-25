import difflib

def compare_texts(expected_text, user_text):

    if not expected_text or not user_text:
        return 100.0, 100.0

    expected_text = expected_text.strip()
    user_text = user_text.strip()

    # Character similarity
    char_similarity = difflib.SequenceMatcher(
        None, expected_text, user_text
    ).ratio()

    char_diff = (1 - char_similarity) * 100

    # Word similarity
    expected_words = expected_text.split()
    user_words = user_text.split()

    word_similarity = difflib.SequenceMatcher(
        None, expected_words, user_words
    ).ratio()

    word_diff = (1 - word_similarity) * 100

    return round(word_diff, 2), round(char_diff, 2)