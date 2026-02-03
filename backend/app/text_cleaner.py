"""
Simple rule-based text cleaner to remove common stuttering patterns.

Goals:
- Remove filler words (uh, um, er, ah, like, you know)
- Collapse immediate word repetitions (e.g., "I I I want" -> "I want")
- Handle hyphenated / partial repetitions (e.g., "b-b-because" -> "because")
- Preserve overall meaning and sentence structure
"""

import re
from typing import List

FILLERS = {
    "uh", "uhh", "uhhh",
    "um", "umm", "ummm",
    "er", "err", "errr",
    "ah", "ahh", "ahhh",
    "hmm", "hmmm",
    "like", "like like",
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
    """
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)


def _detokenize(tokens: List[str]) -> str:
    """
    Simple detokenization: join words with spaces, but not before punctuation.
    """
    out = []
    for i, tok in enumerate(tokens):
        if i > 0 and tok not in {".", ",", "!", "?", ":", ";"}:
            out.append(" ")
        out.append(tok)
    return "".join(out)


def clean_stuttered_text(raw_text: str) -> str:
    """
    Enhanced cleaning function with better stutter pattern detection.
    """
    if not raw_text or not raw_text.strip():
        return ""
    
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
            prev_prev_word = ""
            prev_word = ""
        cleaned_tokens.append(tok)

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
    
    return cleaned.strip()





