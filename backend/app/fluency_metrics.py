"""
Rule-based Fluency & Clarity Metrics Calculator

This module calculates fluency scores using simple, explainable rules.
Perfect for academic evaluation - no ML, just clear logic.

Metrics:
1. Word Repetitions - Counts immediate word repetitions
2. Filler Words - Counts common fillers (uh, um, etc.)
3. Pauses - Estimates pauses from audio silence

Fluency Score:
- Starts at 100%
- Deducts points for each disfluency
- Simple and explainable for viva/presentation
"""

import re
from typing import Dict, Tuple
import numpy as np


# Common filler words for counting
FILLER_WORDS = {
    "uh", "uhh", "uhhh",
    "um", "umm", "ummm",
    "er", "err", "errr",
    "ah", "ahh", "ahhh",
    "hmm", "hmmm",
    "like",
    "you know",
    "i mean",
    "sort of", "sorta",
    "kind of", "kinda",
    "well",
    "so",
    "actually",
    "basically",
}

# Common grammar error patterns
GRAMMAR_ERROR_PATTERNS = [
    # Duplicate verbs
    (r'\b(is|are|was|were)\s+(is|are|was|were)\b', 'duplicate verb'),
    
    # Article errors
    (r'\b(a)\s+([aeiou])', 'a before vowel'),  # Should be "an"
    (r'\b(an)\s+([^aeiou])', 'an before consonant'),  # Should be "a"
    
    # Double negatives
    (r'\b(don\'t|doesn\'t|didn\'t)\s+(not)\b', 'double negative'),
    
    # Pronoun errors
    (r'\b(me|him|her|them)\s+(and)\s+(I|he|she|they)\b', 'incorrect pronoun order'),
    
    # Subject-verb agreement errors
    (r'\b(I|you|we|they)\s+(is|was)\b', 'subject-verb disagreement'),
    (r'\b(he|she|it)\s+(are|were)\b', 'subject-verb disagreement'),
    
    # Word order errors (common in stuttered speech)
    (r'\b(good|fine|okay|happy|sad|tired|busy)\s+(I|you|he|she|we|they)\s+(am|is|are|was|were)\b', 'incorrect word order'),
    (r'\bI\s+am\s+name\s+(is|was)\b', 'incorrect phrase - should be "my name"'),
    (r'\bI\s+am\s+name\b', 'incorrect phrase - should be "my name"'),
    
    # Redundant words
    (r'\bthat\s+do\s+that\b', 'redundant words'),
    (r'\bfor\s+process\s+what\b', 'nonsensical phrase'),
]


def count_word_repetitions(text: str) -> int:
    """
    Count immediate word repetitions in text.
    
    Example: "I I I want" -> 2 repetitions (I appears 3 times, so 2 extra)
    
    Returns: Number of repeated words
    """
    if not text:
        return 0
    
    # Tokenize to words only
    words = re.findall(r'\b\w+\b', text.lower())
    
    if len(words) < 2:
        return 0
    
    repetitions = 0
    prev_word = ""
    
    for word in words:
        if word == prev_word:
            repetitions += 1
        prev_word = word
    
    return repetitions


def count_filler_words(text: str) -> int:
    """
    Count filler words in text.
    
    Returns: Number of filler word occurrences
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    count = 0
    
    # Count each filler word
    for filler in FILLER_WORDS:
        # Use word boundaries to avoid partial matches
        pattern = rf'\b{re.escape(filler)}\b'
        matches = len(re.findall(pattern, text_lower))
        count += matches
    
    return count


def count_grammar_errors(text: str) -> int:
    """
    Count basic grammar errors in text using simple pattern matching.
    
    Returns: Number of grammar errors detected
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    error_count = 0
    
    # Check each grammar error pattern
    for pattern, _ in GRAMMAR_ERROR_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        error_count += len(matches)
    
    return error_count


def estimate_pauses_from_audio(audio: np.ndarray, sample_rate: int, 
                                silence_threshold: float = 0.02,
                                min_pause_duration: float = 0.3) -> int:
    """
    Estimate number of pauses in audio based on silence detection.
    
    Args:
        audio: Audio waveform (numpy array)
        sample_rate: Sample rate in Hz
        silence_threshold: Amplitude threshold for silence (default: 0.02)
        min_pause_duration: Minimum duration for a pause in seconds (default: 0.3)
    
    Returns: Number of detected pauses
    """
    if len(audio) == 0:
        return 0
    
    # Convert to absolute values
    abs_audio = np.abs(audio)
    
    # Find silent regions (below threshold)
    is_silent = abs_audio < silence_threshold
    
    # Find transitions from speech to silence and back
    # This is a simple approach: count continuous silent regions
    pause_count = 0
    in_silence = False
    silence_start = 0
    
    min_samples = int(min_pause_duration * sample_rate)
    
    for i in range(len(is_silent)):
        if is_silent[i]:
            if not in_silence:
                silence_start = i
                in_silence = True
        else:
            if in_silence:
                # Check if silence was long enough to be a pause
                silence_duration = i - silence_start
                if silence_duration >= min_samples:
                    pause_count += 1
                in_silence = False
    
    # Check if audio ends in silence
    if in_silence:
        silence_duration = len(is_silent) - silence_start
        if silence_duration >= min_samples:
            pause_count += 1
    
    return pause_count


def calculate_fluency_score(repetitions: int, fillers: int, pauses: int,
                           total_words: int) -> float:
    """
    Calculate fluency score using simple rule-based deduction.
    
    Scoring Logic (explainable for viva):
    - Start from 100%
    - Deduct 2 points per repetition
    - Deduct 1 point per filler word
    - Deduct 1 point per pause
    - Normalize by total words to avoid penalizing longer speech
    
    Args:
        repetitions: Number of word repetitions
        fillers: Number of filler words
        pauses: Number of pauses
        total_words: Total word count
    
    Returns: Fluency score (0-100)
    """
    if total_words == 0:
        return 0.0
    
    # Base score
    score = 100.0
    
    # Deduct points for disfluencies
    # Weighted by total words to normalize
    if total_words > 0:
        repetition_penalty = (repetitions * 2.0) / total_words * 100
        filler_penalty = (fillers * 1.0) / total_words * 100
        pause_penalty = (pauses * 1.0) / total_words * 100
        
        score -= repetition_penalty
        score -= filler_penalty
        score -= pause_penalty
    
    # Ensure score is between 0 and 100
    score = max(0.0, min(100.0, score))
    
    return round(score, 2)


def calculate_metrics_for_text(text: str) -> Dict[str, int]:
    """
    Calculate all text-based metrics.
    
    Returns: Dictionary with metrics
    """
    if not text:
        return {
            "repetitions": 0,
            "fillers": 0,
            "grammar_errors": 0,
            "total_words": 0,
        }
    
    repetitions = count_word_repetitions(text)
    fillers = count_filler_words(text)
    grammar_errors = count_grammar_errors(text)
    total_words = len(re.findall(r'\b\w+\b', text.lower()))
    
    return {
        "repetitions": repetitions,
        "fillers": fillers,
        "grammar_errors": grammar_errors,
        "total_words": total_words,
    }


def calculate_metrics_for_audio(audio: np.ndarray, sample_rate: int) -> Dict[str, int]:
    """
    Calculate audio-based metrics (pauses).
    
    Returns: Dictionary with pause count
    """
    pauses = estimate_pauses_from_audio(audio, sample_rate)
    
    return {
        "pauses": pauses,
    }


def calculate_fluency_metrics(raw_text: str, cleaned_text: str,
                              raw_audio: np.ndarray, sample_rate: int) -> Dict:
    """
    Calculate complete fluency metrics for before/after comparison.
    
    This is the main function used by the API.
    
    Returns: Dictionary with all metrics for before and after
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Calculate metrics for raw (before) text
    raw_metrics = calculate_metrics_for_text(raw_text)
    raw_audio_metrics = calculate_metrics_for_audio(raw_audio, sample_rate)
    
    logger.info(f"Raw text grammar errors: {raw_metrics['grammar_errors']}")
    
    # Calculate metrics for cleaned (after) text
    cleaned_metrics = calculate_metrics_for_text(cleaned_text)
    
    logger.info(f"Cleaned text grammar errors: {cleaned_metrics['grammar_errors']}")
    
    # Calculate fluency scores
    raw_score = calculate_fluency_score(
        raw_metrics["repetitions"],
        raw_metrics["fillers"],
        raw_audio_metrics["pauses"],
        raw_metrics["total_words"]
    )
    
    cleaned_score = calculate_fluency_score(
        cleaned_metrics["repetitions"],
        cleaned_metrics["fillers"],
        0,  # Assume pauses are reduced (we don't have cleaned audio)
        cleaned_metrics["total_words"]
    )
    
    result = {
        "before": {
            "repetitions": raw_metrics["repetitions"],
            "fillers": raw_metrics["fillers"],
            "pauses": raw_audio_metrics["pauses"],
            "grammar_errors": raw_metrics["grammar_errors"],
            "total_words": raw_metrics["total_words"],
            "fluency_score": raw_score,
        },
        "after": {
            "repetitions": cleaned_metrics["repetitions"],
            "fillers": cleaned_metrics["fillers"],
            "pauses": 0,  # Not calculated for cleaned audio
            "grammar_errors": cleaned_metrics["grammar_errors"],
            "total_words": cleaned_metrics["total_words"],
            "fluency_score": cleaned_score,
        },
        "improvement": {
            "repetitions_reduced": raw_metrics["repetitions"] - cleaned_metrics["repetitions"],
            "fillers_reduced": raw_metrics["fillers"] - cleaned_metrics["fillers"],
            "grammar_errors_fixed": raw_metrics["grammar_errors"] - cleaned_metrics["grammar_errors"],
            "score_improvement": cleaned_score - raw_score,
        }
    }
    
    logger.info(f"Metrics calculated - Before grammar: {result['before']['grammar_errors']}, After grammar: {result['after']['grammar_errors']}, Fixed: {result['improvement']['grammar_errors_fixed']}")
    
    return result




