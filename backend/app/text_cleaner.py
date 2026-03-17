"""
<<<<<<< HEAD
Enhanced rule-based text cleaner with grammar and spelling correction.

Goals:
- Remove filler words (uh, um, er, ah, like, you know)
- Collapse immediate word repetitions (e.g., "hi hi hi hello" -> "hi hello")
- Fix common spelling errors
- Improve grammar and sentence structure
- Handle hyphenated / partial repetitions (e.g., "b-b-because" -> "because")
- Preserve overall meaning
"""

import re
from typing import List, Set
try:
    from spellchecker import SpellChecker
    SPELL_CHECKER_AVAILABLE = True
except ImportError:
    SPELL_CHECKER_AVAILABLE = False
    print("Warning: pyspellchecker not available. Install with: pip install pyspellchecker")
=======
Simple rule-based text cleaner to remove common stuttering patterns.

Goals:
- Remove filler words (uh, um, er, ah, like, you know)
- Collapse immediate word repetitions (e.g., "I I I want" -> "I want")
- Handle hyphenated / partial repetitions (e.g., "b-b-because" -> "because")
- Preserve overall meaning and sentence structure
"""

import re
from typing import List
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461

FILLERS = {
    "uh", "uhh", "uhhh",
    "um", "umm", "ummm",
    "er", "err", "errr",
    "ah", "ahh", "ahhh",
    "hmm", "hmmm",
<<<<<<< HEAD
=======
    "like", "like like",
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    "you know", "ya know",
    "i mean", "i mean i mean",
    "sort of", "sorta",
    "kind of", "kinda",
    "well", "well well",
    "so", "so so",
    "actually", "actually actually",
    "basically", "basically basically",
}


def _remove_partial_repetitions(word: str) -> str:
    """
    Simplistic handler for things like "b-b-because" -> "because".
    We collapse repeated leading characters separated by hyphens.
    """
    if "-" in word:
        parts = [p for p in word.split("-") if p]
        if len(parts) > 1 and all(len(p) == 1 for p in parts[:-1]):
            # Take the last part as the full word
            return parts[-1]
    return word


def _tokenize(text: str) -> List[str]:
    """
    Basic tokenization that keeps punctuation as separate tokens.
<<<<<<< HEAD
    Preserves contractions like "didn't", "won't", "I'm".
    """
    # Match words (including contractions with apostrophes) or punctuation
    return re.findall(r"\w+(?:'\w+)?|[^\w\s]", text, re.UNICODE)
=======
    """
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461


def _detokenize(tokens: List[str]) -> str:
    """
    Simple detokenization: join words with spaces, but not before punctuation.
<<<<<<< HEAD
    Handles contractions properly (no space before apostrophe).
    """
    out = []
    for i, tok in enumerate(tokens):
        # Don't add space before punctuation or if this is the first token
        if i > 0 and tok not in {".", ",", "!", "?", ":", ";", "'"}:
            # Also don't add space if previous token was an apostrophe (for contractions)
            if i > 0 and tokens[i-1] != "'":
                out.append(" ")
=======
    """
    out = []
    for i, tok in enumerate(tokens):
        if i > 0 and tok not in {".", ",", "!", "?", ":", ";"}:
            out.append(" ")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        out.append(tok)
    return "".join(out)


<<<<<<< HEAD
def _correct_spelling(text: str) -> str:
    """
    Correct common spelling errors using spell checker.
    Only corrects obvious errors, preserves intentional words.
    """
    if not SPELL_CHECKER_AVAILABLE or not text:
        return text
    
    try:
        spell = SpellChecker()
        # Find all words with their positions
        word_matches = list(re.finditer(r'\b\w+\b', text))
        
        # Process from end to start to avoid offset issues
        corrections = []
        for match in reversed(word_matches):
            word = match.group()
            start, end = match.span()
            
            # Skip very short words, numbers, and proper nouns (capitalized)
            if len(word) <= 2 or word.isdigit() or (word[0].isupper() and len(word) > 1):
                continue
            
            # Check if word is misspelled
            if word.lower() not in spell:
                # Get correction
                correction = spell.correction(word.lower())
                if correction and correction != word.lower() and len(correction) > 0:
                    # Preserve original capitalization
                    if word[0].isupper():
                        corrected_word = correction.capitalize()
                    else:
                        corrected_word = correction
                    
                    corrections.append((start, end, corrected_word))
        
        # Apply corrections from start to end
        corrected_text = text
        for start, end, corrected_word in corrections:
            corrected_text = corrected_text[:start] + corrected_word + corrected_text[end:]
            
    except Exception as e:
        # If spell checking fails, return original text
        pass
    
    return corrected_text


def _fix_nonsensical_patterns(text: str) -> str:
    """
    Fix common nonsensical patterns that result from ASR errors or heavy stuttering.
    These are patterns that are grammatically incorrect and don't make semantic sense.
    """
    if not text:
        return ""
    
    # Fix "I am name is" -> "My name is"
    text = re.sub(r'\bI\s+am\s+name\s+is\b', 'My name is', text, flags=re.IGNORECASE)
    text = re.sub(r'\bI\s+am\s+name\b', 'My name', text, flags=re.IGNORECASE)
    
    # Remove redundant "that" patterns
    # "keep that do that" -> "keep that" or "do that"
    text = re.sub(r'\bkeep\s+that\s+do\s+that\b', 'keep that', text, flags=re.IGNORECASE)
    text = re.sub(r'\bkeep\s+that\s+do\b', 'keep', text, flags=re.IGNORECASE)
    
    # Fix "for process" -> "to process" or remove
    text = re.sub(r'\bfor\s+process\s+what\b', 'what', text, flags=re.IGNORECASE)
    text = re.sub(r'\bfor\s+process\b', 'to process', text, flags=re.IGNORECASE)
    
    # Remove meaningless "that do" patterns
    text = re.sub(r'\bthat\s+do\s+for\b', 'for', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthat\s+do\s+that\b', 'that', text, flags=re.IGNORECASE)
    
    # Fix "what we didn't deliver matches" -> "what we didn't deliver"
    text = re.sub(r'\bdeliver\s+matches\s+and\b', 'deliver and', text, flags=re.IGNORECASE)
    
    # Remove duplicate "that" with different words in between
    text = re.sub(r'\bthat\s+(\w+)\s+that\b', r'that \1', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def _fix_grammar_errors(text: str) -> str:
    """
    Fix common grammar errors using rule-based patterns.
    Explainable and simple for academic presentation.
    """
    if not text:
        return ""
    
    # Fix standalone 'i' pronoun to 'I' (but not in words like "it", "is")
    text = re.sub(r"\bi\b", "I", text)
    
    # Fix word order issues (Subject-Verb-Object corrections)
    word_order_fixes = [
        # "Good I am" -> "I am good"
        (r"\b(good|fine|okay|ok|well|great|happy|sad|tired|busy)\s+(I|i)\s+(am|was)\b", r"\2 \3 \1"),
        # "Happy I am" -> "I am happy"
        (r"\b(excited|confused|ready|done|finished)\s+(I|i)\s+(am|was)\b", r"\2 \3 \1"),
        # "There I am" -> "I am there" (location)
        (r"\b(here|there)\s+(I|i)\s+(am|was)\b", r"\2 \3 \1"),
        # "Going I am" -> "I am going"
        (r"\b(going|coming|leaving|staying|working|studying)\s+(I|i)\s+(am|was)\b", r"\2 \3 \1"),
        # "Good you are" -> "You are good"
        (r"\b(good|fine|okay|ok|well|great)\s+(you|he|she|we|they)\s+(are|were|is|was)\b", r"\2 \3 \1"),
        # "Ready you are" -> "You are ready"
        (r"\b(ready|done|finished|busy|tired)\s+(you|he|she|we|they)\s+(are|were|is|was)\b", r"\2 \3 \1"),
    ]
    
    for pattern, replacement in word_order_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Fix common contractions / typos (expanded list)
    contractions = {
        "im": "I'm",
        "dont": "don't",
        "cant": "can't",
        "wont": "won't",
        "ive": "I've",
        "id": "I'd",
        "ill": "I'll",
        "isnt": "isn't",
        "arent": "aren't",
        "didnt": "didn't",
        "wasnt": "wasn't",
        "werent": "weren't",
        "hasnt": "hasn't",
        "havent": "haven't",
        "wouldnt": "wouldn't",
        "couldnt": "couldn't",
        "shouldnt": "shouldn't",
        "youre": "you're",
        "theyre": "they're",
        "were": "we're",  # Context-dependent
        "lets": "let's",
        "thats": "that's",
        "whats": "what's",
        "wheres": "where's",
        "whos": "who's",
        "shes": "she's",
        "hes": "he's",
    }
    
    for wrong, right in contractions.items():
        pattern = rf"\b{wrong}\b"
        text = re.sub(pattern, right, text, flags=re.IGNORECASE)
    
    # Fix common word errors and misspellings
    word_fixes = {
        r"\byour\s+welcom\b": "you're welcome",
        r"\bteh\b": "the",
        r"\badn\b": "and",
        r"\btahn\b": "than",
        r"\bno\b": "know",  # Context-dependent, but common
        r"\bwat\b": "what",
        r"\bwut\b": "what",
        r"\bwht\b": "what",
        r"\bthru\b": "through",
        r"\btho\b": "though",
        r"\bcuz\b": "because",
        r"\bcause\b": "because",  # If missing "be"
    }
    
    for pattern, replacement in word_fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Fix "its" vs "it's" - if followed by verb, likely "it's"
    text = re.sub(r"\bits\s+(is|was|will|would|can|could|should|has|had)\b", r"it's \1", text, flags=re.IGNORECASE)
    
    # Fix double spaces and normalize
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def _remove_phrase_repetitions(text: str) -> str:
    """
    Remove repeated phrases within the same sentence.
    Example: "I am good, I am good" -> "I am good"
    """
    if not text:
        return ""
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'([.!?])', text)
    cleaned_sentences = []
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
            
        sentence = sentences[i].strip()
        punct = sentences[i + 1] if i + 1 < len(sentences) else ""
        
        if not sentence:
            continue
        
        # Split sentence by commas to get phrases
        phrases = [p.strip() for p in sentence.split(',')]
        
        # Remove duplicate consecutive phrases
        unique_phrases = []
        prev_phrase = ""
        
        for phrase in phrases:
            # Normalize for comparison (lowercase, remove extra spaces)
            normalized = ' '.join(phrase.lower().split())
            prev_normalized = ' '.join(prev_phrase.lower().split())
            
            # Skip if same as previous phrase
            if normalized and normalized != prev_normalized:
                unique_phrases.append(phrase)
                prev_phrase = phrase
            elif not normalized:
                continue
        
        # Reconstruct sentence
        if unique_phrases:
            cleaned_sentence = ', '.join(unique_phrases)
            cleaned_sentences.append(cleaned_sentence + punct)
    
    return ' '.join(cleaned_sentences)


def _improve_sentence_structure(text: str) -> str:
    """
    Improve sentence structure: capitalization, punctuation, spacing.
    """
    if not text:
        return ""
    
    # Remove phrase repetitions first
    text = _remove_phrase_repetitions(text)
    
    # Split into sentences based on punctuation
    raw_sentences = re.split(r"([.!?]+)", text)
    sentences: List[str] = []

    i = 0
    while i < len(raw_sentences):
        part = raw_sentences[i].strip()
        if not part:
            i += 1
            continue
        punct = ""
        if i + 1 < len(raw_sentences) and re.fullmatch(r"[.!?]+", raw_sentences[i + 1]):
            punct = raw_sentences[i + 1].strip()
            i += 1

        # Capitalize first letter of sentence
        if part:
            part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
        # Ensure sentence ends with punctuation
        if not punct:
            punct = "."
        sentences.append(part + punct)
        i += 1

    normalized = " ".join(sentences)
    
    # Final cleanup
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _basic_grammar_normalization(text: str) -> str:
    """
    Enhanced grammar normalization with spelling correction.
    """
    if not text:
        return ""
    
    # Step 1: Fix nonsensical patterns first
    text = _fix_nonsensical_patterns(text)
    
    # Step 2: Fix grammar errors
    text = _fix_grammar_errors(text)
    
    # Step 3: Correct spelling
    text = _correct_spelling(text)
    
    # Step 4: Improve sentence structure
    text = _improve_sentence_structure(text)
    
    return text


def clean_stuttered_text(raw_text: str, apply_grammar_correction: bool = True) -> str:
    """
    Enhanced cleaning function with advanced stutter pattern detection and optional grammar correction.
    Handles: "hi hi hi hello how are are you" -> "Hi hello how are you."
    
    Args:
        raw_text: Raw text from ASR
        apply_grammar_correction: Whether to apply grammar correction (default: True)
    
    Returns:
        Cleaned text with optional grammar correction
=======
def clean_stuttered_text(raw_text: str) -> str:
    """
    Enhanced cleaning function with better stutter pattern detection.
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    """
    if not raw_text or not raw_text.strip():
        return ""
    
<<<<<<< HEAD
    # Step 1: Initial normalization
    text = raw_text.lower().strip()
    
    # Step 2: Remove multi-word fillers (longest first to avoid partial matches)
    for phrase in sorted(FILLERS, key=len, reverse=True):
        pattern = rf"\b{re.escape(phrase)}\b"
        text = re.sub(pattern, "", text)

    # Step 3: Handle partial word repetitions like "b-b-because", "th-th-that"
    text = re.sub(r'\b(\w)-(\1-)*(\1+)\b', r'\3', text)
    
    # Step 4: Handle character repetitions within words (e.g., "sooo" -> "so")
    # But preserve valid words like "too", "see", "bee"
    text = re.sub(r'(\w)\1{2,}', r'\1', text)

    # Step 5: Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    if not text:
        return ""

    # Step 6: Tokenize and remove repetitions
    tokens = _tokenize(text)
    tokens = [_remove_partial_repetitions(t) for t in tokens]

    # Step 7: Advanced repetition removal with context awareness
    cleaned_tokens: List[str] = []
    prev_word: str = ""
    prev_prev_word: str = ""
    word_count = {}  # Track word frequency to avoid removing valid repetitions
    
    for tok in tokens:
        if tok.isalpha():
            tok_lower = tok.lower()
            word_count[tok_lower] = word_count.get(tok_lower, 0) + 1
            
            # Skip if same as previous word (immediate repetition)
            # This handles: "hi hi hi" -> "hi", "are are" -> "are"
            if tok_lower == prev_word.lower():
                continue
            
            # Skip if same as two words ago (A B A pattern) for very common stutter words
            if tok_lower == prev_prev_word.lower() and prev_word != "":
                common_stutter_words = {"i", "the", "a", "an", "is", "are", "was", "were", 
                                       "it", "this", "that", "to", "and", "or", "but", "hi",
                                       "hello", "how", "what", "when", "where", "why", "who"}
                if tok_lower in common_stutter_words and len(tok_lower) <= 5:
                    continue
            
            # Update tracking
            prev_prev_word = prev_word
            prev_word = tok_lower
        else:
            # Reset on punctuation (allows same word in different sentences)
=======
    text = raw_text.lower().strip()

    # Remove multi-word fillers first (longest first to avoid partial matches)
    for phrase in sorted(FILLERS, key=len, reverse=True):
        # Remove with word boundaries, handle multiple occurrences
        pattern = rf"\b{re.escape(phrase)}\b"
        while re.search(pattern, text):
            text = re.sub(pattern, "", text, count=1)

    # Handle partial word repetitions like "b-b-because", "th-th-that"
    text = re.sub(r'\b(\w)-(\1-)*(\1+)\b', r'\3', text)  # b-b-because -> because
    
    # Handle character repetitions within words (e.g., "sooo" -> "so")
    text = re.sub(r'(\w)\1{2,}', r'\1', text)  # sooo -> so, but keep "too" as is

    # Normalize extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    tokens = _tokenize(text)

    # Apply partial repetition cleanup
    tokens = [_remove_partial_repetitions(t) for t in tokens]

    # Collapse immediate word repetitions (case-insensitive) with lookback
    cleaned_tokens: List[str] = []
    prev_word: str = ""
    prev_prev_word: str = ""
    
    for tok in tokens:
        if tok.isalpha():
            # Skip if same as previous word (immediate repetition)
            if tok == prev_word:
                continue
            # Skip if same as two words ago (A B A pattern)
            if tok == prev_prev_word and prev_word != "":
                continue
            prev_prev_word = prev_word
            prev_word = tok
        else:
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            prev_prev_word = ""
            prev_word = ""
        cleaned_tokens.append(tok)

<<<<<<< HEAD
    # Step 8: Reconstruct text
    cleaned = _detokenize(cleaned_tokens)
    
    # Step 9: Remove standalone filler words (but be careful with "like" - only remove as filler)
    # Remove "like" only when it's clearly a filler (not followed by a noun/verb)
    cleaned = re.sub(r'\b(uh|um|er|ah|hmm|eh|oh)\b', '', cleaned, flags=re.IGNORECASE)
    
    # Remove "like" only when used as filler (e.g., "I was like really tired")
    # But keep "I like pizza", "I would like to", etc.
    cleaned = re.sub(r'\blike\s+(really|totally|super|very|so|kinda|sorta)\b', r'\1', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(was|were|is|are)\s+like\s+(really|totally|super|very|so)\b', r'\1 \2', cleaned, flags=re.IGNORECASE)
    
    # Step 10: Normalize spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    # Step 11: Apply grammar and spelling correction (ONLY if enabled)
    if apply_grammar_correction:
        cleaned = _basic_grammar_normalization(cleaned)
    else:
        # Just capitalize first letter and add period if missing
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
            if not cleaned.endswith(('.', '!', '?')):
                cleaned += '.'
=======
    # Final tidy-up
    cleaned = _detokenize(cleaned_tokens)
    
    # Remove standalone filler words that might have been missed
    cleaned = re.sub(r'\b(uh|um|er|ah|hmm)\b', '', cleaned, flags=re.IGNORECASE)
    
    # Normalize spaces again
    cleaned = re.sub(r"\s+", " ", cleaned)
    
    # Capitalize first letter
    cleaned = cleaned.strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    
    return cleaned.strip()





