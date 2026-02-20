"""
Test grammar correction for word order issues
"""
from app.text_cleaner import clean_stuttered_text

# Test cases
test_cases = [
    ("Hello, how are you? Good I am.", "Expected: Hello, how are you? I am good."),
    ("Good I am", "Expected: I am good"),
    ("Fine I am", "Expected: I am fine"),
    ("Happy I am", "Expected: I am happy"),
    ("Tired I am", "Expected: I am tired"),
    ("Good you are", "Expected: You are good"),
    ("Ready you are", "Expected: You are ready"),
    ("Going I am", "Expected: I am going"),
    ("Here I am", "Expected: I am here"),
    ("There I am", "Expected: I am there"),
    ("Hello hello how are are you", "Expected: Hello how are you"),
    ("I I I am am good", "Expected: I am good"),
]

print("\n" + "="*80)
print("GRAMMAR CORRECTION TEST")
print("="*80)

for i, (original, expected) in enumerate(test_cases, 1):
    cleaned = clean_stuttered_text(original)
    print(f"\nTest {i}:")
    print(f"  Original: {original}")
    print(f"  Cleaned:  {cleaned}")
    print(f"  {expected}")
    print("-" * 80)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
