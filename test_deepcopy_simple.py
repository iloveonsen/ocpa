"""
Simple deepcopy test without full OCEL loading.
"""
import sys
sys.path.insert(0, '/home/user/ocpa')

import copy
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

print("="*70)
print("Simple OCPN Deepcopy Test")
print("="*70)

# Create a simple OCPN manually
print("\n1. Creating simple OCPN...")
ocpn = ObjectCentricPetriNet(name="test_net")

# Add places
p1 = ObjectCentricPetriNet.Place("p1", "order", initial=True)
p2 = ObjectCentricPetriNet.Place("p2", "order")
p3 = ObjectCentricPetriNet.Place("p3", "order", final=True)

ocpn.places.add(p1)
ocpn.places.add(p2)
ocpn.places.add(p3)

# Add transition
t1 = ObjectCentricPetriNet.Transition("t1", "Place Order", silent=False)
t2 = ObjectCentricPetriNet.Transition("t2", "Confirm Order", silent=False)

ocpn.transitions.add(t1)
ocpn.transitions.add(t2)

# Add arcs
arc1 = ObjectCentricPetriNet.Arc(p1, t1, weight=1, variable=False)
arc2 = ObjectCentricPetriNet.Arc(t1, p2, weight=1, variable=False)
arc3 = ObjectCentricPetriNet.Arc(p2, t2, weight=1, variable=False)
arc4 = ObjectCentricPetriNet.Arc(t2, p3, weight=1, variable=False)

ocpn.arcs.add(arc1)
ocpn.arcs.add(arc2)
ocpn.arcs.add(arc3)
ocpn.arcs.add(arc4)

print(f"   Places: {len(ocpn.places)}")
print(f"   Transitions: {len(ocpn.transitions)}")
print(f"   Arcs: {len(ocpn.arcs)}")

# Check connections before deepcopy
print("\n2. Checking original connections...")
print(f"   p1: in_arcs={len(p1.in_arcs)}, out_arcs={len(p1.out_arcs)}")
print(f"   p2: in_arcs={len(p2.in_arcs)}, out_arcs={len(p2.out_arcs)}")
print(f"   p3: in_arcs={len(p3.in_arcs)}, out_arcs={len(p3.out_arcs)}")
print(f"   t1: in_arcs={len(t1.in_arcs)}, out_arcs={len(t1.out_arcs)}")
print(f"   t2: in_arcs={len(t2.in_arcs)}, out_arcs={len(t2.out_arcs)}")

# Perform deepcopy
print("\n3. Performing deepcopy...")
try:
    ocpn_copy = copy.deepcopy(ocpn)
    print("   ✓ Deepcopy succeeded")
except Exception as e:
    print(f"   ✗ Deepcopy failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"   Places: {len(ocpn_copy.places)}")
print(f"   Transitions: {len(ocpn_copy.transitions)}")
print(f"   Arcs: {len(ocpn_copy.arcs)}")

# Check connections after deepcopy
print("\n4. Checking copied connections...")
for place in ocpn_copy.places:
    print(f"   {place.name}: in_arcs={len(place.in_arcs)}, out_arcs={len(place.out_arcs)}, initial={place.initial}, final={place.final}")

for trans in ocpn_copy.transitions:
    print(f"   {trans.name}: in_arcs={len(trans.in_arcs)}, out_arcs={len(trans.out_arcs)}, silent={trans.silent}")

# Verification
print("\n5. Verification:")
checks = []

# Check counts
if len(ocpn.places) == len(ocpn_copy.places):
    print("   ✓ Place count matches")
    checks.append(True)
else:
    print(f"   ✗ Place count: {len(ocpn.places)} → {len(ocpn_copy.places)}")
    checks.append(False)

if len(ocpn.transitions) == len(ocpn_copy.transitions):
    print("   ✓ Transition count matches")
    checks.append(True)
else:
    print(f"   ✗ Transition count: {len(ocpn.transitions)} → {len(ocpn_copy.transitions)}")
    checks.append(False)

if len(ocpn.arcs) == len(ocpn_copy.arcs):
    print("   ✓ Arc count matches")
    checks.append(True)
else:
    print(f"   ✗ Arc count: {len(ocpn.arcs)} → {len(ocpn_copy.arcs)}")
    checks.append(False)

# Check initial place
initial_places = [p for p in ocpn_copy.places if p.initial]
if len(initial_places) == 1 and len(initial_places[0].out_arcs) > 0:
    print(f"   ✓ Initial place has {len(initial_places[0].out_arcs)} outgoing arc(s)")
    checks.append(True)
else:
    print(f"   ✗ Initial place issue")
    checks.append(False)

# Check final place
final_places = [p for p in ocpn_copy.places if p.final]
if len(final_places) == 1 and len(final_places[0].in_arcs) > 0:
    print(f"   ✓ Final place has {len(final_places[0].in_arcs)} incoming arc(s)")
    checks.append(True)
else:
    print(f"   ✗ Final place issue")
    checks.append(False)

# Check silent flag
silent_preserved = all(
    orig_t.silent == copy_t.silent
    for orig_t, copy_t in zip(sorted(ocpn.transitions, key=lambda x: x.name),
                              sorted(ocpn_copy.transitions, key=lambda x: x.name))
)
if silent_preserved:
    print("   ✓ Silent flags preserved")
    checks.append(True)
else:
    print("   ✗ Silent flags not preserved")
    checks.append(False)

# Check that arcs are properly connected
total_expected_connections = len(ocpn.arcs) * 2  # Each arc should be in source.out and target.in
total_actual_connections = sum(len(p.in_arcs) + len(p.out_arcs) for p in ocpn_copy.places)
total_actual_connections += sum(len(t.in_arcs) + len(t.out_arcs) for t in ocpn_copy.transitions)

if total_expected_connections == total_actual_connections:
    print(f"   ✓ Arc connections correct ({total_actual_connections} connections)")
    checks.append(True)
else:
    print(f"   ✗ Arc connections: expected {total_expected_connections}, got {total_actual_connections}")
    checks.append(False)

# Final result
print("\n" + "="*70)
if all(checks):
    print("✓ ALL CHECKS PASSED - Deepcopy is working correctly")
else:
    print("✗ SOME CHECKS FAILED - Deepcopy has issues")
    print("\nDeepcopy issues can cause 'Algorithmic error' in Dijkstra!")
print("="*70)
