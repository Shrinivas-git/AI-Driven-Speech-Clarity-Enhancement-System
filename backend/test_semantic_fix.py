"""
Test semantic/nonsensical pattern fixes
"""
from app.text_cleaner import clean_stuttered_text

# Test cases
test_cases = [
    ("We will keep that do that for process what we didn't deliver matches and we are the champion",
     "Expected: We will keep what we didn't deliver and we are the champion."),
    ("I want to keep that do that", "Expected: I want to keep that."),
    ("We need for process the data", "Expected: We need to process the data."),
    ("The file deliver matches and works", "Expected: The file deliver and works."),
    ("Hello, hello, I am good, good I am.", "Expected: Hello, I am good."),
]

print("\n" + "="*80)
print("SEMANTIC/NONSENSICAL PATTERN FIX TEST")
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
