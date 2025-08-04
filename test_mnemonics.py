import pandas as pd
import random
from mnemonic_generator import process_words, generate_mnemonic, CIPHER

def setup_test_data():
    """Set up test fixtures: a small DataFrame with sample words."""
    random.seed(42)  # Ensure reproducible random choices
    sample_words = ["big", "dog", "run", "red", "cat", "jump"]
    return process_words(sample_words, CIPHER)

def test_valid_number():
    """Test mnemonic generation for a valid number."""
    df = setup_test_data()
    phrase = generate_mnemonic("123", df)
    assert phrase is not None, "Expected a phrase for valid number"
    assert "the" in phrase, "Expected filler word in phrase"

def test_invalid_number():
    """Test mnemonic generation for an invalid (non-digit) number."""
    df = setup_test_data()
    phrase = generate_mnemonic("12a3", df)
    assert phrase is None, "Expected None for invalid number"

def test_no_match():
    """Test mnemonic generation for a number with no matching phrase."""
    df = setup_test_data()
    phrase = generate_mnemonic("999999", df)
    assert phrase is None, "Expected None for unmatchable number"

def test_single_word():
    """Test mnemonic generation for a single-word phrase."""
    df = setup_test_data()
    phrase = generate_mnemonic("9", df)
    assert phrase is not None, "Expected a phrase for single digit"
    assert phrase.startswith("the "), "Expected filler word"

def test_two_words():
    """Test mnemonic generation for a two-word phrase."""
    df = setup_test_data()
    phrase = generate_mnemonic("12", df)
    assert phrase is not None, "Expected a phrase for two digits"
    assert len(phrase.split()) >= 2, "Expected at least two words"

def test_three_words():
    """Test mnemonic generation for a three-word phrase."""
    df = setup_test_data()
    phrase = generate_mnemonic("123", df)
    assert phrase is not None, "Expected a phrase for three digits"
    assert len(phrase.split()) >= 3, "Expected at least three words"