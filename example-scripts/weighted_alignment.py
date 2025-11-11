"""
Example script demonstrating weighted alignment calculation.

This script shows how to use the new weighted alignment functions to calculate
object-centric alignments with activity-specific weights.
"""

from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.algo.conformance.alignments import algorithm as alignment_factory
from ocpa.algo.conformance.alignments.alignment import (
    create_weighted_cost_function,
    create_custom_cost_function,
    default_cost_function
)

# Load OCEL and discover OCPN
filename = "sample_logs/jsonocel/order_process.jsonocel"
ocel = ocel_import_factory.apply(filename)
ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})

print("="*80)
print("Object-Centric Alignment: Weighted vs. Standard Comparison")
print("="*80)

# 1. Calculate standard alignments (for comparison)
print("\n1. Calculating standard alignments...")
standard_alignments = alignment_factory.calculate_oc_alignments(ocel, ocpn)

print(f"   Total variants: {len(standard_alignments)}")
for variant_id, alignment in list(standard_alignments.items())[:3]:  # Show first 3
    print(f"   Variant {variant_id}: cost = {alignment.get_cost():.2f}, moves = {len(alignment.moves)}")

# 2. Calculate weighted alignments with activity weights
print("\n2. Calculating weighted alignments...")
print("   Using weight formula: cost = len(objects) * (1 + weight)")

# Define activity weights (these should sum to 1.0 for relative weighting)
# Higher weight = more important activity = higher cost for deviations
activity_weights = {
    "place order": 0.3,      # 30% importance
    "confirm order": 0.2,    # 20% importance
    "item out of stock": 0.1,  # 10% importance
    "reorder item": 0.1,     # 10% importance
    "pick item": 0.15,       # 15% importance
    "send package": 0.15     # 15% importance
}

print(f"   Activity weights: {activity_weights}")

weighted_alignments = alignment_factory.calculate_oc_alignments_with_weights(
    ocel, ocpn, activity_weights
)

print(f"   Total variants: {len(weighted_alignments)}")
for variant_id, alignment in list(weighted_alignments.items())[:3]:  # Show first 3
    print(f"   Variant {variant_id}: cost = {alignment.get_cost():.2f}, moves = {len(alignment.moves)}")

# 3. Compare costs for same variant
print("\n3. Detailed comparison for first variant:")
first_variant_id = list(standard_alignments.keys())[0]
standard_align = standard_alignments[first_variant_id]
weighted_align = weighted_alignments[first_variant_id]

print(f"\n   Variant ID: {first_variant_id}")
print(f"   Standard alignment cost: {standard_align.get_cost():.2f}")
print(f"   Weighted alignment cost: {weighted_align.get_cost():.2f}")
print(f"   Cost difference: {weighted_align.get_cost() - standard_align.get_cost():.2f}")

print("\n   Move-by-move comparison:")
print("   " + "-"*70)
print(f"   {'Move Type':<20} {'Activity':<25} {'Objects':<10} {'Std Cost':>10} {'Weighted':>10}")
print("   " + "-"*70)

for std_move, wgt_move in zip(standard_align.moves, weighted_align.moves):
    move_type = "Sync" if std_move.log_move and std_move.model_move else \
                ("Log" if std_move.log_move else "Model")
    activity = std_move.log_move or std_move.model_move or "N/A"
    num_objects = len(std_move.objects) if std_move.objects else 0

    print(f"   {move_type:<20} {activity:<25} {num_objects:<10} {std_move.cost:>10.2f} {wgt_move.cost:>10.2f}")

# 4. Using custom cost function with different formula
print("\n4. Using custom cost function (quadratic formula):")
print("   Formula: cost = (num_objects^2) * (1 + weight)")

# Create custom cost function with quadratic formula
quadratic_formula = lambda num_obj, weight: (num_obj ** 2) * (1 + weight)
custom_cost_fn_creator = create_custom_cost_function(quadratic_formula)
custom_cost_fn = custom_cost_fn_creator(activity_weights)

custom_alignments = alignment_factory.calculate_oc_alignments_with_cost_function(
    ocel, ocpn, custom_cost_fn
)

custom_align = custom_alignments[first_variant_id]
print(f"\n   Variant ID: {first_variant_id}")
print(f"   Standard alignment cost: {standard_align.get_cost():.2f}")
print(f"   Weighted alignment cost: {weighted_align.get_cost():.2f}")
print(f"   Custom (quadratic) cost: {custom_align.get_cost():.2f}")

# 5. Using cost function directly
print("\n5. Direct cost function usage:")
cost_fn = create_weighted_cost_function(activity_weights)

# Calculate cost for example scenarios
scenarios = [
    ("place order", ["order_1"], False),
    ("pick item", ["order_1", "item_1", "item_2"], False),
    ("send package", ["order_1"], False),
]

print("   Example cost calculations:")
for activity, objects, is_silent in scenarios:
    cost = cost_fn(activity, objects, is_silent)
    weight = activity_weights.get(activity, 0.0)
    base_cost = len(objects)
    print(f"   {activity:<25} objects={len(objects)}, weight={weight:.2f} → cost={cost:.2f} (base={base_cost})")

print("\n" + "="*80)
print("Weighted alignment calculation completed successfully!")
print("="*80)
