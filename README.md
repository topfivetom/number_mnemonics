# Mnemonic Phrase Generator

This project generates memorable phrases from number strings using a consonant-based cipher inspired by the Major System. It maps digits to consonants, strips vowels from common English words, and constructs grammatically coherent phrases (e.g., "the big dog runs") with optional filler words (articles, prepositions). The codebase is split into three files for modularity: core logic, word list management, and tests.

## Features
- Converts number strings (e.g., "123") into phrases like "the big dog runs".
- Uses a Major System cipher to map digits to consonants.
- Categorizes words into adjectives, nouns, and verbs for coherent phrases.
- Saves and loads a word list locally to avoid repeated network requests.
- Includes a test suite using `pytest`.
- Generates a word length distribution plot and saves processed data to a CSV.

## Installation
1. **Clone the Repository** (or create the files from provided code):
   ```bash
   git clone <repository-url>
   cd mnemonic-generator
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` includes:
   - pandas
   - requests
   - matplotlib
   - nltk

4. **Download NLTK Data**:
   Run the script once to download NLTK's WordNet and tagger data:
   ```bash
   python mnemonic_generator.py
   ```

## Usage
1. **Generate a Mnemonic Phrase**:
   ```bash
   python mnemonic_generator.py --number 123
   ```
   Example output:
   ```
   Number: 123 -> Phrase: the big dog runs
   ```

2. **Run Tests**:
   ```bash
   pytest test_mnemonics.py -v
   ```

3. **Output Files**:
   - `common_words.txt`: Local copy of the word list (created after first run).
   - `mnemonic_words.csv`: Processed words with number sequences and parts of speech.
   - `word_lengths.png`: Plot of word length distributions.

## Project Structure
- `mnemonic_generator.py`: Core logic for processing words, generating mnemonics, and CLI input.
- `word_list_manager.py`: Handles fetching and saving the word list.
- `test_mnemonics.py`: Tests for the mnemonic generator, compatible with `pytest`.
- `requirements.txt`: Dependency list.
- `README.md`: This file.

## Major System Cipher
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

## Notes
- Requires Python 3.6+ and an internet connection for the initial word list fetch.
- The word list is sourced from [google-10000-english](https://github.com/first20hours/google-10000-english).
- Tests use a small sample dataset for speed; real runs use the full 1000-word list.