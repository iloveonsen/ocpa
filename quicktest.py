# core import of the alignment calculation algorithm
from ocpa.algo.conformance.alignments.algorithm import calculate_oc_alignment_given_variant_id

# general ocpa import to help setting up testing environments
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory_json
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

# imports for evaluation
import timeit
import tracemalloc

from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.visualization.alignment_viz.visualization import alignment_viz
from ocpa.algo.conformance.alignments.alignment import (
    Alignment, Move, DefinedModelMove, UndefinedModelMove,
    SynchronousMove, UndefinedSynchronousMove, LogMove
)

from datetime import datetime
import matplotlib.pyplot as plt

from ocpa.algo.util.filtering.log.variant_filtering import filter_infrequent_variants
from ocpa.algo.util.filtering.log.activity_filtering import filter_infrequent_activities

# Sample log file path - update this to your actual file
filename = "sample-logs/bpi2017/BPI2017-Final.csv"
object_types = ["application", "offer"]
parameters = {
    "obj_names": object_types,
    "val_names": [],
    "act_name": "event_activity",
    "time_name": "event_timestamp",
    "sep": ","
}

print("Import started")
ocel = ocel_import_factory.apply(file_path=filename, parameters=parameters)
print("Import done")

# Filter infrequent activities and variants
filtered_ocel_activities = filter_infrequent_activities(ocel, 0.5)
filtered_ocel = filter_infrequent_variants(filtered_ocel_activities, 0.5)

# Construct de jure OCPN with silent transitions
dejure_ocpn = ObjectCentricPetriNet(name="Silent Transition")

# Add places
p1 = ObjectCentricPetriNet.Place(name="p1", object_type="application", initial=True)
dejure_ocpn.places.add(p1)
p2 = ObjectCentricPetriNet.Place(name="p2", object_type="application")
dejure_ocpn.places.add(p2)
p3 = ObjectCentricPetriNet.Place(name="p3", object_type="application")
dejure_ocpn.places.add(p3)
p4 = ObjectCentricPetriNet.Place(name="p4", object_type="application", final=True)
dejure_ocpn.places.add(p4)
p5 = ObjectCentricPetriNet.Place(name="p5", object_type="offer", initial=True)
dejure_ocpn.places.add(p5)
p6 = ObjectCentricPetriNet.Place(name="p6", object_type="offer")
dejure_ocpn.places.add(p6)
p7 = ObjectCentricPetriNet.Place(name="p7", object_type="offer")
dejure_ocpn.places.add(p7)
p8 = ObjectCentricPetriNet.Place(name="p8", object_type="offer", final=True)
dejure_ocpn.places.add(p8)

# Add transitions
t1 = ObjectCentricPetriNet.Transition(name="Create application", label="Create application")
dejure_ocpn.transitions.add(t1)
t2 = ObjectCentricPetriNet.Transition(name="Accept", label="Accept")
dejure_ocpn.transitions.add(t2)
t3 = ObjectCentricPetriNet.Transition(name="Create offer", label="Create offer")
dejure_ocpn.transitions.add(t3)
t4 = ObjectCentricPetriNet.Transition(name="Send (mail and online)", label="Send (mail and online)")
dejure_ocpn.transitions.add(t4)
t5 = ObjectCentricPetriNet.Transition(name="Call", label="Call")
dejure_ocpn.transitions.add(t5)
t6 = ObjectCentricPetriNet.Transition(name="Validate", label="Validate")
dejure_ocpn.transitions.add(t6)
t7 = ObjectCentricPetriNet.Transition(name="s1", label="s1", silent=True)
dejure_ocpn.transitions.add(t7)
t8 = ObjectCentricPetriNet.Transition(name="s2", label="s2", silent=True)
dejure_ocpn.transitions.add(t8)

# Add arcs
# 1-5
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p1, t1))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t1, p2))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p2, t2))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p5, t3))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t2, p3))
# 6-10
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p3, t3))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t3, p3))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t3, p6))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p6, t4))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p3, t5))
# 11-15
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t5, p3))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p3, t6))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t8, p3))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t4, p7))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p7, t5))
# 16-20
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p7, t7))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t5, p8))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t7, p8))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(t6, p4))
dejure_ocpn.add_arc(ObjectCentricPetriNet.Arc(p4, t8))

# Calculate Alignments
print(f"Total variants: {len(filtered_ocel.variants_dict)}")

for variant_key in filtered_ocel.variants_dict.keys():
    print(f"Start Alignment calculation for variant: {variant_key}")

    # Track memory usage
    tracemalloc.start()
    start_time = timeit.default_timer()

    # Calculate alignment
    alignment = calculate_oc_alignment_given_variant_id(
        filtered_ocel,
        dejure_ocpn,
        variant_key,
        date_format='%Y-%m-%d %H:%M:%S.%f'
    )

    # Print timing and memory info
    elapsed_time = timeit.default_timer() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Done with alignment calculation")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

    # Visualize alignment
    alignment_viz(alignment)

    # Only process first variant as demonstration
    break

print("Quicktest completed")
