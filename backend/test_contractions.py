"""
Test contraction handling
"""
from app.text_cleaner import clean_stuttered_text

# Test cases
test_cases = [
    ("We will keep that do that for process what we didn't deliver matches and we are the champion", 
     "Expected: We will keep that do for process what we didn't deliver matches and we are the champion."),
    ("I didn't do it", "Expected: I didn't do it."),
    ("We won't go there", "Expected: We won't go there."),
    ("She can't believe it", "Expected: She can't believe it."),
    ("They're coming tomorrow", "Expected: They're coming tomorrow."),
    ("I'm going to the store", "Expected: I'm going to the store."),
    ("It's a beautiful day", "Expected: It's a beautiful day."),
    ("We've been waiting", "Expected: We've been waiting."),
    ("You'll see tomorrow", "Expected: You'll see tomorrow."),
]

print("\n" + "="*80)
print("CONTRACTION HANDLING TEST")
print("="*80)

for i, (original, expected) in enumerate(test_cases, 1):
    cleaned = clean_stuttered_text(original)
    print(f"\nTest {i}:")
    print(f"  Original: {original}")
    print(f"  Cleaned:  {cleaned}")
    print(f"  {expected}")
    
    # Check if contractions are preserved
    if "'" in original and "' " in cleaned:
        print(f"  ⚠️  WARNING: Contraction broken!")
    elif "'" in original and "'" in cleaned:
        print(f"  ✓ Contraction preserved")
    
    print("-" * 80)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
