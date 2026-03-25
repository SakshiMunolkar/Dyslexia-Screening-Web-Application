import random
import os


DATASET_DIR = "dataset"

CHAR_FILE = os.path.join(DATASET_DIR, "file1.txt")
WORD_FILE = os.path.join(DATASET_DIR, "file2.txt")
SENTENCE_FILE = os.path.join(DATASET_DIR, "sentences.txt")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")


def _load_lines(filepath: str):

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if not lines:
        raise ValueError(f"No valid content found in {filepath}")

    return lines


# CHARACTER TEST
def load_random_character() -> str:
    """
    Returns a random single character from file1.txt
    """
    characters = _load_lines(CHAR_FILE)
    return random.choice(characters)


# WORD TEST
def load_random_word() -> str:    
    words = _load_lines(WORD_FILE)
    return random.choice(words)


# SENTENCE TEST
def load_random_sentence() -> str:
    sentences = _load_lines(SENTENCE_FILE)
    return random.choice(sentences)


# IMAGE TEST
def load_random_training_image() -> str:
    if not os.path.exists(TRAIN_DIR):
        raise FileNotFoundError(f"Training directory not found: {TRAIN_DIR}")

    images = [
        file for file in os.listdir(TRAIN_DIR)
        if file.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not images:
        raise ValueError("No images found in training directory.")

    random_image = random.choice(images)

    return os.path.join(TRAIN_DIR, random_image)