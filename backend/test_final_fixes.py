"""
Test final fixes: "I am name" correction and conditional grammar correction
"""
from app.text_cleaner import clean_stuttered_text

print("\n" + "="*80)
print("TEST 1: 'I am name' correction")
print("="*80)

test1 = "I am name is A.B.C."
result1_with_grammar = clean_stuttered_text(test1, apply_grammar_correction=True)
result1_without_grammar = clean_stuttered_text(test1, apply_grammar_correction=False)

print(f"\nOriginal: {test1}")
print(f"With grammar correction:    {result1_with_grammar}")
print(f"Without grammar correction: {result1_without_grammar}")
print(f"\nExpected with grammar:    My name is A. B. C.")
print(f"Expected without grammar: I am name is a. b. c.")

print("\n" + "="*80)
print("TEST 2: Grammar correction toggle")
print("="*80)

test2 = "Good I am, hello hello"
result2_with_grammar = clean_stuttered_text(test2, apply_grammar_correction=True)
result2_without_grammar = clean_stuttered_text(test2, apply_grammar_correction=False)

print(f"\nOriginal: {test2}")
print(f"With grammar correction:    {result2_with_grammar}")
print(f"Without grammar correction: {result2_without_grammar}")
print(f"\nExpected with grammar:    I am good, hello.")
print(f"Expected without grammar: good i am, hello.")

print("\n" + "="*80)
print("TEST 3: Complex sentence")
print("="*80)

test3 = "We will keep that do that for process what we didn't deliver matches and we are the champion"
result3_with_grammar = clean_stuttered_text(test3, apply_grammar_correction=True)
result3_without_grammar = clean_stuttered_text(test3, apply_grammar_correction=False)

print(f"\nOriginal: {test3}")
print(f"With grammar correction:    {result3_with_grammar}")
print(f"Without grammar correction: {result3_without_grammar}")

print("\n" + "="*80)
print("TESTS COMPLETE")
print("="*80 + "\n")
