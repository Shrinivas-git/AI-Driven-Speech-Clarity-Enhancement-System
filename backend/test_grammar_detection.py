"""
Test grammar error detection
"""
from app.fluency_metrics import count_grammar_errors

test_cases = [
    ("I am name is A.B.C.", "Should detect 'I am name is'"),
    ("Good I am", "Should detect word order error"),
    ("I is happy", "Should detect subject-verb disagreement"),
    ("He are coming", "Should detect subject-verb disagreement"),
    ("That do that for process", "Should detect redundant words"),
    ("A apple is red", "Should detect 'a' before vowel"),
    ("An book is here", "Should detect 'an' before consonant"),
    ("I don't not like it", "Should detect double negative"),
    ("Hello, how are you?", "Should detect 0 errors"),
    ("My name is John", "Should detect 0 errors"),
]

print("\n" + "="*80)
print("GRAMMAR ERROR DETECTION TEST")
print("="*80)

for i, (text, expected) in enumerate(test_cases, 1):
    errors = count_grammar_errors(text)
    print(f"\nTest {i}:")
    print(f"  Text: {text}")
    print(f"  Errors detected: {errors}")
    print(f"  {expected}")
    print("-" * 80)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
