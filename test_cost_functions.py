"""
Direct test of cost function utilities without full ocpa imports.
"""

# Import only the alignment module directly
import sys
import importlib.util

# Load alignment.py directly
spec = importlib.util.spec_from_file_location(
    "alignment",
    "/home/user/ocpa/ocpa/algo/conformance/alignments/alignment.py"
)
alignment_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment_module)

# Extract functions
default_cost_function = alignment_module.default_cost_function
create_weighted_cost_function = alignment_module.create_weighted_cost_function
create_custom_cost_function = alignment_module.create_custom_cost_function

print("="*70)
print("Testing Weighted Alignment Cost Functions")
print("="*70)

# Test 1: Default cost function
print("\n1. Testing default_cost_function...")
cost = default_cost_function("test_activity", ["obj1", "obj2"], False)
print(f"   Input: activity='test_activity', objects=['obj1', 'obj2'], is_silent=False")
print(f"   Output cost: {cost}")
print(f"   Expected: 2 (number of objects)")
assert cost == 2, f"Expected 2, got {cost}"
print("   ✓ PASS")

cost_silent = default_cost_function("test_activity", ["obj1"], True)
print(f"   Input: activity='test_activity', objects=['obj1'], is_silent=True")
print(f"   Output cost: {cost_silent}")
print(f"   Expected: 0.001 (silent transition)")
assert cost_silent == 0.001, f"Expected 0.001, got {cost_silent}"
print("   ✓ PASS")

# Test 2: Weighted cost function
print("\n2. Testing create_weighted_cost_function...")
weights = {
    "Create Order": 0.3,
    "Pack Order": 0.5,
    "Ship Order": 0.2
}
print(f"   Weights: {weights}")
weighted_cost_fn = create_weighted_cost_function(weights)

# Test with weighted activity
cost = weighted_cost_fn("Create Order", ["obj1", "obj2"], False)
expected = 2 * (1 + 0.3)  # 2.6
print(f"   Input: activity='Create Order', objects=2, weight=0.3")
print(f"   Formula: 2 * (1 + 0.3) = {expected}")
print(f"   Output cost: {cost}")
assert abs(cost - expected) < 0.001, f"Expected {expected}, got {cost}"
print("   ✓ PASS")

# Test with unweighted activity
cost = weighted_cost_fn("Unknown Activity", ["obj1"], False)
expected = 1 * (1 + 0.0)  # 1.0
print(f"   Input: activity='Unknown Activity', objects=1, weight=0.0 (default)")
print(f"   Formula: 1 * (1 + 0.0) = {expected}")
print(f"   Output cost: {cost}")
assert abs(cost - expected) < 0.001, f"Expected {expected}, got {cost}"
print("   ✓ PASS")

# Test 3: Custom cost function
print("\n3. Testing create_custom_cost_function...")
print("   Formula: (num_objects^2) * (1 + weight)")
quadratic_formula = lambda num_obj, weight: (num_obj ** 2) * (1 + weight)
custom_cost_fn_creator = create_custom_cost_function(quadratic_formula)
custom_cost_fn = custom_cost_fn_creator(weights)

cost = custom_cost_fn("Create Order", ["obj1", "obj2", "obj3"], False)
expected = (3 ** 2) * (1 + 0.3)  # 9 * 1.3 = 11.7
print(f"   Input: activity='Create Order', objects=3, weight=0.3")
print(f"   Formula: (3^2) * (1 + 0.3) = {expected}")
print(f"   Output cost: {cost}")
assert abs(cost - expected) < 0.001, f"Expected {expected}, got {cost}"
print("   ✓ PASS")

# Test 4: Edge cases
print("\n4. Testing edge cases...")

# Empty objects list
cost = default_cost_function("test", [], False)
print(f"   Empty objects list: cost = {cost} (should be 1)")
assert cost == 1, f"Expected 1, got {cost}"
print("   ✓ PASS")

# None objects
cost = default_cost_function("test", None, False)
print(f"   None objects: cost = {cost} (should be 1)")
assert cost == 1, f"Expected 1, got {cost}"
print("   ✓ PASS")

# Multiple objects with high weight
weighted_fn = create_weighted_cost_function({"High": 0.9})
cost = weighted_fn("High", ["o1", "o2", "o3", "o4", "o5"], False)
expected = 5 * (1 + 0.9)  # 9.5
print(f"   5 objects with 0.9 weight: cost = {cost} (expected {expected})")
assert abs(cost - expected) < 0.001, f"Expected {expected}, got {cost}"
print("   ✓ PASS")

# Test 5: Practical example
print("\n5. Practical example: Order processing costs...")
activity_weights = {
    "place order": 0.3,
    "confirm order": 0.2,
    "pick item": 0.15,
    "send package": 0.15,
    "item out of stock": 0.1,
    "reorder item": 0.1
}
cost_fn = create_weighted_cost_function(activity_weights)

scenarios = [
    ("place order", ["order_1"], 1 * 1.3),
    ("pick item", ["order_1", "item_1", "item_2"], 3 * 1.15),
    ("send package", ["order_1"], 1 * 1.15),
    ("unknown_activity", ["obj_1"], 1 * 1.0),
]

print("   Activity                 Objects  Weight  Expected  Actual")
print("   " + "-"*60)
for activity, objects, expected in scenarios:
    actual = cost_fn(activity, objects, False)
    weight = activity_weights.get(activity, 0.0)
    print(f"   {activity:<24} {len(objects):<8} {weight:<7.2f} {expected:<9.2f} {actual:.2f}")
    assert abs(actual - expected) < 0.001, f"Expected {expected}, got {actual}"
print("   ✓ ALL PASS")

print("\n" + "="*70)
print("ALL TESTS PASSED! ✓")
print("="*70)
print("\nSummary:")
print("  - Default cost function: ✓")
print("  - Weighted cost function: ✓")
print("  - Custom cost function: ✓")
print("  - Edge cases: ✓")
print("  - Practical examples: ✓")
print("\nThe weighted alignment cost functions are working correctly!")
