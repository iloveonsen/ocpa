"""
Evaluation runner for collecting alignment statistics across all variants.

This script processes all variants in the filtered BPI2017 dataset and collects
detailed statistics about each alignment calculation including:
- Event and object counts
- Alignment costs
- Move type distributions (log/model/sync)
- Move sequences
- Execution times

Results are saved to a CSV file for further analysis.
"""

# Core alignment imports
from ocpa.algo.conformance.alignments.algorithm import calculate_oc_alignment_given_variant_id
from ocpa.algo.conformance.alignments.alignment import (
    Alignment, Move, DefinedModelMove, UndefinedModelMove,
    SynchronousMove, UndefinedSynchronousMove, LogMove
)

# OCPA imports
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.algo.util.filtering.log.variant_filtering import filter_infrequent_variants
from ocpa.algo.util.filtering.log.activity_filtering import filter_infrequent_activities

# Data processing and timing
import pandas as pd
import timeit
from datetime import datetime
from typing import Dict, List

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

print("=" * 80)
print("ALIGNMENT EVALUATION RUNNER")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Import OCEL
print("Importing OCEL from CSV...")
ocel = ocel_import_factory.apply(file_path=filename, parameters=parameters)
print(f"✓ Import complete: {len(ocel.log.log)} events")
print()

# Filter infrequent activities and variants
print("Filtering infrequent activities (threshold: 0.5)...")
filtered_ocel_activities = filter_infrequent_activities(ocel, 0.5)
print(f"✓ Activities filtered")

print("Filtering infrequent variants (threshold: 0.5)...")
filtered_ocel = filter_infrequent_variants(filtered_ocel_activities, 0.5)
print(f"✓ Variants filtered: {len(filtered_ocel.variants_dict)} variants remain")
print()

# Construct de jure OCPN with silent transitions
print("Constructing de jure OCPN...")
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

print(f"✓ OCPN constructed: {len(dejure_ocpn.places)} places, {len(dejure_ocpn.transitions)} transitions")
print()

# Calculate Alignments and collect statistics
print("=" * 80)
print("PROCESSING VARIANTS")
print("=" * 80)

results = []
total_variants = len(filtered_ocel.variants_dict)
completed = 0
failed = 0

for variant_key in filtered_ocel.variants_dict.keys():
    try:
        # Get variant information
        indirect_id = filtered_ocel.variants_dict[variant_key][0]
        process_execution = filtered_ocel.process_executions[indirect_id]
        num_events = len(process_execution)

        # Get unique objects for this variant
        process_execution_objects = filtered_ocel.process_execution_objects[indirect_id]
        unique_objects = set()
        for obj_type, obj_id in process_execution_objects:
            unique_objects.add(obj_id)
        num_objects = len(unique_objects)

        # Start timing
        start_time = timeit.default_timer()

        # Calculate alignment
        alignment = calculate_oc_alignment_given_variant_id(
            filtered_ocel,
            dejure_ocpn,
            variant_key,
            date_format='%Y-%m-%d %H:%M:%S.%f'
        )

        # Calculate execution time
        execution_time = timeit.default_timer() - start_time

        # Analyze moves
        num_log_moves = 0
        num_model_moves = 0
        num_sync_moves = 0
        move_sequence = []

        for move in alignment.moves:
            if isinstance(move, LogMove):
                num_log_moves += 1
                move_sequence.append(f"L:{move.log_move}")
            elif isinstance(move, DefinedModelMove):
                num_model_moves += 1
                move_sequence.append(f"M:{move.model_move}")
            elif isinstance(move, SynchronousMove):
                num_sync_moves += 1
                move_sequence.append(f"S:{move.model_move}")
            else:
                # Catch any other move types
                move_sequence.append(f"U:{type(move).__name__}")

        move_sequence_str = "|".join(move_sequence)

        # Store result
        results.append({
            'variant_id': variant_key,
            'num_events': num_events,
            'num_objects': num_objects,
            'alignment_cost': alignment.get_cost(),
            'num_log_moves': num_log_moves,
            'num_model_moves': num_model_moves,
            'num_sync_moves': num_sync_moves,
            'total_moves': len(alignment.moves),
            'move_sequence': move_sequence_str,
            'execution_time': execution_time
        })

        completed += 1

        # Print progress
        if completed % 10 == 0:
            print(f"Progress: {completed}/{total_variants} variants processed "
                  f"({completed/total_variants*100:.1f}%)")

    except Exception as e:
        failed += 1
        print(f"✗ Failed variant {variant_key}: {str(e)}")
        # Store failed result with error info
        results.append({
            'variant_id': variant_key,
            'num_events': -1,
            'num_objects': -1,
            'alignment_cost': -1,
            'num_log_moves': -1,
            'num_model_moves': -1,
            'num_sync_moves': -1,
            'total_moves': -1,
            'move_sequence': f"ERROR: {str(e)}",
            'execution_time': -1
        })

print()
print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print(f"Total variants: {total_variants}")
print(f"Completed: {completed}")
print(f"Failed: {failed}")
print()

# Create DataFrame
df = pd.DataFrame(results)

# Save to CSV
output_filename = f"alignment_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(output_filename, index=False)
print(f"✓ Results saved to: {output_filename}")
print()

# Print statistics (only for successful alignments)
successful_df = df[df['alignment_cost'] >= 0]

if len(successful_df) > 0:
    print("Statistical Summary (successful alignments):")
    print("-" * 80)
    print(successful_df[['num_events', 'num_objects', 'alignment_cost',
                         'num_log_moves', 'num_model_moves', 'num_sync_moves',
                         'execution_time']].describe())
    print()

    print("Top 5 most costly alignments:")
    print("-" * 80)
    print(successful_df.nlargest(5, 'alignment_cost')[['variant_id', 'num_events',
                                                         'num_objects', 'alignment_cost',
                                                         'execution_time']])
    print()

    print("Top 5 longest execution times:")
    print("-" * 80)
    print(successful_df.nlargest(5, 'execution_time')[['variant_id', 'num_events',
                                                         'num_objects', 'alignment_cost',
                                                         'execution_time']])

print()
print("=" * 80)
print(f"Evaluation complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
