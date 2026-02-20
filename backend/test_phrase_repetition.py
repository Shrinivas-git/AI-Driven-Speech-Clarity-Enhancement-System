"""
Test phrase repetition removal
"""
from app.text_cleaner import clean_stuttered_text

# Test cases
test_cases = [
    ("Hello, hello, I am good, good I am.", "Expected: Hello, I am good."),
    ("I am good, I am good.", "Expected: I am good."),
    ("Hello, hello, how are you, how are you.", "Expected: Hello, how are you."),
    ("I like pizza, I like pizza, I like pizza.", "Expected: I like pizza."),
    ("Good morning, good morning.", "Expected: Good morning."),
    ("How are you, I am fine, I am fine.", "Expected: How are you, I am fine."),
    ("Hello, I am good, I am good, thank you.", "Expected: Hello, I am good, thank you."),
]

print("\n" + "="*80)
print("PHRASE REPETITION REMOVAL TEST")
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
