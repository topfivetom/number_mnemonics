import requests
import os
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
Word List Manager

Fetches and saves a list of common English words from a URL or loads them from a local file.
Used by the mnemonic generator to avoid repeated network requests.
"""

WORDS_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears.txt"
WORDS_FILE = "common_words.txt"
MAX_WORDS = 1000

def fetch_common_words(url: str, max_words: int = MAX_WORDS) -> List[str]:
    """Fetch common English words from a URL.

    Args:
        url (str): URL to the word list.
        max_words (int): Maximum number of words to fetch (default: 1000).

    Returns:
        List[str]: List of lowercase alphabetic words.

    Example:
        words = fetch_common_words(WORDS_URL)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        words = response.text.splitlines()[:max_words]
        logging.info(f"Fetched {len(words)} common words from {url}")
        return [w.lower() for w in words if w.isalpha()]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch words from {url}: {e}")
        return []

def save_words(words: List[str], filename: str = WORDS_FILE) -> None:
    """Save words to a local file.

    Args:
        words (List[str]): List of words to save.
        filename (str): Path to the output file (default: common_words.txt).

    Example:
        save_words(["big", "dog"], "common_words.txt")
    """
    with open(filename, 'w') as f:
        f.write('\n'.join(words))
    logging.info(f"Saved {len(words)} words to {filename}")

def load_words(filename: str = WORDS_FILE, url: str = WORDS_URL, max_words: int = MAX_WORDS) -> List[str]:
    """Load words from a local file or fetch from URL if not available.

    Args:
        filename (str): Path to the local word file (default: common_words.txt).
        url (str): URL to fetch words if local file is missing.
        max_words (int): Maximum number of words to fetch (default: 1000).

    Returns:
        List[str]: List of words.

    Example:
        words = load_words()
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            words = f.read().splitlines()
        logging.info(f"Loaded {len(words)} words from {filename}")
        return words
    else:
        words = fetch_common_words(url, max_words)
        if words:
            save_words(words, filename)
        return words