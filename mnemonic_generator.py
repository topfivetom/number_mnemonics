import pandas as pd
import re
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
import logging
import random
import argparse
import nltk
from nltk.corpus import wordnet
from word_list_manager import load_words

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download NLTK data (run once during setup)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

"""
Mnemonic Phrase Generator

Generates memorable phrases from number strings using a consonant-based cipher inspired by the Major System.
Maps digits to consonants, strips vowels from common English words, and constructs grammatically coherent phrases
(e.g., adjective-noun-verb) with optional filler words (articles, prepositions). Supports command-line input and
processes words from a local or remote word list.

Cipher (Major System):
- 0: z, s, c (soft c)
- 1: d, t
- 2: n
- 3: m
- 4: r
- 5: l
- 6: j, sh, ch, g (soft g)
- 7: k, c (hard), g (hard), q, qu
- 8: f, v, th
- 9: b, p

Usage:
    python mnemonic_generator.py --number <number>
    Example: python mnemonic_generator.py --number 123
"""

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
VOWELS = r"[aeiou]"
FILLER_WORDS = ["the", "a", "of", "in", "and"]

def get_part_of_speech(word: str) -> Optional[str]:
    """Determine the part of speech for a word using NLTK and WordNet.

    Args:
        word (str): Word to classify.

    Returns:
        Optional[str]: 'adj' (adjective), 'noun', 'verb', or None if unknown.

    Example:
        get_part_of_speech("big") -> "adj"
    """
    synsets = wordnet.synsets(word)
    if not synsets:
        return None
    pos = synsets[0].pos()
    if pos == 'a' or pos == 's':  # Adjective or satellite adjective
        return 'adj'
    elif pos == 'n':
        return 'noun'
    elif pos == 'v':
        return 'verb'
    return None

def process_words(words: List[str], cipher: Dict[int, List[str]]) -> pd.DataFrame:
    """Process words: strip vowels, map to cipher numbers, add parts of speech, and compute lengths.

    Args:
        words (List[str]): List of words to process.
        cipher (Dict[int, List[str]]): Mapping of digits to consonants.

    Returns:
        pd.DataFrame: DataFrame with columns: word, no_vowels, number_sequence, word_length, no_vowels_length, pos.

    Example:
        df = process_words(["big", "dog"], CIPHER)
    """
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
            for num, letters in cipher.items():
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
    # Add part of speech
    df["pos"] = df["word"].apply(get_part_of_speech)
    # Filter valid sequences and non-null POS
    df = df[df["number_sequence"].str.match(r"^\d+$") & df["pos"].notnull()]
    return df[["word", "no_vowels", "number_sequence", "word_length", "no_vowels_length", "pos"]]

def generate_mnemonic(number: str, df: pd.DataFrame, max_words: int = 3, use_fillers: bool = True) -> Optional[str]:
    """Generate a grammatically coherent mnemonic phrase from a number string.

    Args:
        number (str): Input number string (digits only).
        df (pd.DataFrame): DataFrame with processed words and parts of speech.
        max_words (int): Maximum number of content words in the phrase (default: 3).
        use_fillers (bool): Whether to include filler words (default: True).

    Returns:
        Optional[str]: A mnemonic phrase (e.g., "the big dog runs") or None if no match is found.

    Example:
        df = process_words(["big", "dog", "run"], CIPHER)
        generate_mnemonic("123", df) -> "the big dog runs"
    """
    if not number.isdigit():
        logging.error(f"Invalid input: {number} must be digits only")
        return None
    n = len(number)
    # Try all possible splits up to max_words
    for words in range(1, min(max_words + 1, n + 1)):
        if words == 1:
            seq = number
            matches = df[(df["number_sequence"] == seq) & (df["pos"] == "noun")]["word"].tolist()
            if matches:
                word = random.choice(matches)
                return f"the {word}" if use_fillers else word
        elif words == 2:
            for i in range(1, n):
                seq1, seq2 = number[:i], number[i:]
                matches1 = df[(df["number_sequence"] == seq1) & (df["pos"] == "adj")]["word"].tolist()
                matches2 = df[(df["number_sequence"] == seq2) & (df["pos"] == "noun")]["word"].tolist()
                if matches1 and matches2:
                    adj, noun = random.choice(matches1), random.choice(matches2)
                    return f"the {adj} {noun}" if use_fillers else f"{adj} {noun}"
        elif words == 3:
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    seq1, seq2, seq3 = number[:i], number[i:j], number[j:]
                    matches1 = df[(df["number_sequence"] == seq1) & (df["pos"] == "adj")]["word"].tolist()
                    matches2 = df[(df["number_sequence"] == seq2) & (df["pos"] == "noun")]["word"].tolist()
                    matches3 = df[(df["number_sequence"] == seq3) & (df["pos"] == "verb")]["word"].tolist()
                    if matches1 and matches2 and matches3:
                        adj, noun, verb = random.choice(matches1), random.choice(matches2), random.choice(matches3)
                        return f"the {adj} {noun} {verb}" if use_fillers else f"{adj} {noun} {verb}"
    logging.warning(f"No mnemonic phrase found for {number}")
    return None

def plot_word_lengths(df: pd.DataFrame) -> None:
    """Plot distribution of word lengths (original and without vowels).

    Args:
        df (pd.DataFrame): DataFrame with word_length and no_vowels_length columns.

    Example:
        plot_word_lengths(df)
    """
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
    """Main function to process words and handle command-line input.

    Parses a number from the command line, generates a mnemonic phrase, and processes the word list.
    """
    parser = argparse.ArgumentParser(description="Generate a mnemonic phrase from a number string.")
    parser.add_argument("--number", type=str, help="Number string to convert to a mnemonic phrase (e.g., '123')")
    args = parser.parse_args()

    # Load words
    words = load_words()
    if not words:
        logging.error("No words loaded. Exiting.")
        return
    df = process_words(words, CIPHER)
    logging.info(f"Processed {len(df)} words with valid number sequences and parts of speech")

    # Plot word lengths
    plot_word_lengths(df)

    # Save DataFrame for reference
    df.to_csv("mnemonic_words.csv", index=False)
    logging.info("Saved processed words to mnemonic_words.csv")

    # Generate mnemonic for command-line input
    if args.number:
        phrase = generate_mnemonic(args.number, df)
        print(f"Number: {args.number} -> Phrase: {phrase or 'Not found'}")

if __name__ == '__main__':
    main()