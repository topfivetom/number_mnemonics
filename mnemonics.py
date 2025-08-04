# # Mnemonic Phrase Generator
# Generates memorable phrases from number strings using a consonant-based cipher, inspired by the Major System.
# Takes a number (e.g., "123") and produces a phrase of common words (e.g., "den rue").
# Uses 1000 common English words from https://github.com/first20hours/google-10000-english.

import pandas as pd
import re
import requests
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
CIPHER = {
    0: ["z", "s", "c"],  # soft c
    1: ["d", "t"],
    2: ["n"],
    3: ["m"],
    4: ["r"],
    5: ["l"],
    6: ["j", "sh", "ch", "g"],  # soft g
    7: ["k", "c", "g", "q", "qu"],  # hard c, hard g
    8: ["f", "v", "th"],
    9: ["b", "p"]
}
WORDS_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears.txt"
VOWELS = r"[aeiou]"

def fetch_common_words(url: str, max_words: int = 1000) -> List[str]:
    """Fetch common words from a URL, returning up to max_words."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        words = response.text.splitlines()[:max_words]
        logging.info(f"Fetched {len(words)} common words from {url}")
        return [w.lower() for w in words if w.isalpha()]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch words from {url}: {e}")
        return []

def process_words(words: List[str], cipher: Dict[int, List[str]]) -> pd.DataFrame:
    """Process words: strip vowels, map to cipher numbers, and compute lengths."""
    df = pd.DataFrame({"word": words})
    # Strip vowels
    df["no_vowels"] = df["word"].str.replace(VOWELS, "", regex=True)
    # Map consonants to numbers
    def map_to_numbers(word: str) -> str:
        result = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and word[i:i+2] in ["sh", "ch", "th", "qu"]:
                consonant = word[i:i+2]
                i += 2
            else:
                consonant = word[i]
                i += 1
            for num, letters in CIPHER.items():
                if consonant in letters:
                    result.append(str(num))
                    break
            else:
                result.append("")  # Non-cipher consonant
        return "".join(result)
    df["number_sequence"] = df["no_vowels"].apply(map_to_numbers)
    # Compute lengths
    df["word_length"] = df["word"].str.len()
    df["no_vowels_length"] = df["no_vowels"].str.len()
    # Filter valid sequences
    df = df[df["number_sequence"].str.match(r"^\d+$")]
    return df[["word", "no_vowels", "number_sequence", "word_length", "no_vowels_length"]]

def generate_mnemonic(number: str, df: pd.DataFrame, max_words: int = 3) -> Optional[str]:
    """Generate a mnemonic phrase from a number string using common words."""
    if not number.isdigit():
        logging.error(f"Invalid input: {number} must be digits only")
        return None
    n = len(number)
    # Try all possible splits up to max_words
    for words in range(1, min(max_words + 1, n + 1)):
        for i in range(n - words + 1):
            for j in range(i + 1, n - words + 2):
                if words == 1:
                    seq = number
                    matches = df[df["number_sequence"] == seq]["word"].tolist()
                    if matches:
                        return random.choice(matches)
                elif words == 2:
                    seq1, seq2 = number[:i], number[i:]
                    matches1 = df[df["number_sequence"] == seq1]["word"].tolist()
                    matches2 = df[df["number_sequence"] == seq2]["word"].tolist()
                    if matches1 and matches2:
                        return f"{random.choice(matches1)} {random.choice(matches2)}"
                elif words == 3:
                    seq1, seq2, seq3 = number[:i], number[i:j], number[j:]
                    matches1 = df[df["number_sequence"] == seq1]["word"].tolist()
                    matches2 = df[df["number_sequence"] == seq2]["word"].tolist()
                    matches3 = df[df["number_sequence"] == seq3]["word"].tolist()
                    if matches1 and matches2 and matches3:
                        return f"{random.choice(matches1)} {random.choice(matches2)} {random.choice(matches3)}"
    logging.warning(f"No mnemonic phrase found for {number}")
    return None

def plot_word_lengths(df: pd.DataFrame) -> None:
    """Plot distribution of word lengths (with and without vowels)."""
    plt.figure(figsize=(10, 5))
    df["no_vowels_length"].value_counts().sort_index().plot(kind='bar', color='#28a745', alpha=0.7, label='No Vowels')
    df["word_length"].value_counts().sort_index().plot(kind='bar', color='#218838', alpha=0.5, label='Original')
    plt.title('Word Length Distribution (Original vs. No Vowels)')
    plt.xlabel('Length')
    plt.ylabel('Count')
    plt.legend()
    plt.savefig('word_lengths.png', bbox_inches='tight')
    plt.show()

def main():
    """Main function to process words and generate mnemonics."""
    # Fetch and process words
    words = fetch_common_words(WORDS_URL)
    if not words:
        return
    df = process_words(words, CIPHER)
    logging.info(f"Processed {len(df)} words with valid number sequences")
    
    # Plot word lengths
    plot_word_lengths(df)
    
    # Test mnemonic generation
    test_numbers = ["123", "456", "7890", "123456", "987654321"]
    for num in test_numbers:
        phrase = generate_mnemonic(num, df)
        print(f"Number: {num} -> Phrase: {phrase or 'Not found'}")
    
    # Save DataFrame for reference
    df.to_csv("mnemonic_words.csv", index=False)
    logging.info("Saved processed words to mnemonic_words.csv")

if __name__ == '__main__':
    main()