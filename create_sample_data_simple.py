"""
Script to create sample data files for weighted alignment testing.
Uses direct JSON manipulation without ocpa dependencies.
"""
import json

# Load the full OCEL
print("Loading order_process.jsonocel...")
with open("alignment/data/order_process.jsonocel", "r") as f:
    full_ocel = json.load(f)

print(f"Total events: {len(full_ocel['ocel:events'])}")
print(f"Total objects: {len(full_ocel['ocel:objects'])}")

# Get all unique activities
activities = set()
for event_id, event_data in full_ocel['ocel:events'].items():
    activities.add(event_data['ocel:activity'])

print(f"\nUnique activities ({len(activities)}):")
for i, act in enumerate(sorted(activities), 1):
    print(f"  {i}. {act}")

# Extract first 10 events for a single trace
event_ids = list(full_ocel['ocel:events'].keys())[:10]
print(f"\nExtracting first {len(event_ids)} events as single trace...")

# Get all objects involved in these events
involved_objects = set()
for event_id in event_ids:
    event_data = full_ocel['ocel:events'][event_id]
    involved_objects.update(event_data['ocel:omap'])

print(f"Objects involved: {len(involved_objects)}")

# Create single trace OCEL
single_trace_data = {
    "ocel:global-event": full_ocel.get("ocel:global-event", {"ocel:activity": "__INVALID__"}),
    "ocel:global-object": full_ocel.get("ocel:global-object", {"ocel:type": "__INVALID__"}),
    "ocel:global-log": full_ocel.get("ocel:global-log", {
        "ocel:attribute-names": [],
        "ocel:object-types": [],
        "ocel:version": "1.0",
        "ocel:ordering": "timestamp"
    }),
    "ocel:events": {},
    "ocel:objects": {}
}

# Add selected events
for event_id in event_ids:
    single_trace_data["ocel:events"][event_id] = full_ocel['ocel:events'][event_id]

# Add involved objects
for obj_id in involved_objects:
    if obj_id in full_ocel['ocel:objects']:
        single_trace_data["ocel:objects"][obj_id] = full_ocel['ocel:objects'][obj_id]

# Save single trace
with open("alignment/data/single_trace.jsonocel", "w") as f:
    json.dump(single_trace_data, f, indent=2)

print("\n✓ Created alignment/data/single_trace.jsonocel")

# Create activity weights - equal weights
num_activities = len(activities)
equal_weight = round(1.0 / num_activities, 4)

activity_weights_equal = {act: equal_weight for act in sorted(activities)}

# Adjust last one to ensure sum is exactly 1.0
activities_list = sorted(activities)
total = sum(activity_weights_equal.values())
activity_weights_equal[activities_list[-1]] += (1.0 - total)

with open("alignment/data/activity_weights.json", "w") as f:
    json.dump(activity_weights_equal, f, indent=2)

print(f"✓ Created alignment/data/activity_weights.json")
print(f"  Each activity has weight: ~{equal_weight:.4f}")
print(f"  Sum of weights: {sum(activity_weights_equal.values()):.6f}")

# Create varied weights (importance-based)
# Assign different weights to different activities
activity_weights_varied = {}
sorted_acts = sorted(activities)

# Example weighting scheme (case-sensitive activity names)
weight_map = {
    "Place Order": 0.25,        # Most important
    "Confirm Order": 0.20,
    "Pick Item": 0.15,
    "Pay Order": 0.12,
    "Start Route": 0.10,
    "Load Cargo": 0.08,
    "End Route": 0.05,
    "Item out of stock": 0.03,
    "Reorder Item": 0.01,
    "Payment Reminder": 0.01
}

# Assign weights, using uniform weight for activities not in weight_map
total_known_weight = 0
unknown_activities = []

for act in sorted_acts:
    if act in weight_map:
        activity_weights_varied[act] = weight_map[act]
        total_known_weight += weight_map[act]
    else:
        unknown_activities.append(act)

# Distribute remaining weight to unknown activities
remaining_weight = 1.0 - total_known_weight
if unknown_activities:
    weight_per_unknown = remaining_weight / len(unknown_activities)
    for act in unknown_activities:
        activity_weights_varied[act] = round(weight_per_unknown, 4)
elif remaining_weight != 0:
    # Adjust last activity if there's rounding error
    activity_weights_varied[sorted_acts[-1]] += remaining_weight

# Normalize to ensure sum is exactly 1.0
total = sum(activity_weights_varied.values())
activity_weights_varied = {k: v/total for k, v in activity_weights_varied.items()}

with open("alignment/data/activity_weights_varied.json", "w") as f:
    json.dump(activity_weights_varied, f, indent=2)

print(f"✓ Created alignment/data/activity_weights_varied.json")
print(f"  Weights range from {min(activity_weights_varied.values()):.4f} to {max(activity_weights_varied.values()):.4f}")
print(f"  Sum of weights: {sum(activity_weights_varied.values()):.6f}")

print("\n" + "="*70)
print("Sample data creation completed!")
print("="*70)
print("\nCreated files:")
print("  1. alignment/data/order_process.jsonocel (full log for OCPN)")
print("  2. alignment/data/single_trace.jsonocel (single trace for alignment)")
print("  3. alignment/data/activity_weights.json (equal weights)")
print("  4. alignment/data/activity_weights_varied.json (varied weights)")
print("\nActivity weights (varied):")
for act, weight in sorted(activity_weights_varied.items(), key=lambda x: -x[1]):
    print(f"  {act:<25} {weight:.4f}")
