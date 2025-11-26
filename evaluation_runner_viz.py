"""
Evaluation runner with visualization support for alignment analysis.

This enhanced version of evaluation_runner.py adds:
- Process execution net visualization for each variant's representative case
- Detailed object tracking (object IDs per variant)
- Activity sequence information
- Visual examples to better understand each variant

Results include both alignment statistics and visualization paths for further analysis.
"""

# Core alignment imports
from ocpa.algo.conformance.alignments.algorithm import (
    calculate_oc_alignment_given_variant_id,
    process_execution_net_from_process_execution
)
from ocpa.algo.conformance.alignments.alignment import (
    Alignment, Move, DefinedModelMove, UndefinedModelMove,
    SynchronousMove, UndefinedSynchronousMove, LogMove
)

# OCPA imports
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.algo.util.filtering.log.variant_filtering import filter_infrequent_variants
from ocpa.algo.util.filtering.log.activity_filtering import filter_infrequent_activities
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory

# Data processing and timing
import pandas as pd
import timeit
import tracemalloc
import os
from datetime import datetime
from typing import Dict, List
from tqdm.auto import tqdm

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

# Create output folders
os.makedirs("evaluation", exist_ok=True)
os.makedirs("evaluation/visualizations", exist_ok=True)

print("=" * 80)
print("ALIGNMENT EVALUATION RUNNER WITH VISUALIZATION")
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

# Visualize de jure net
dejure_gviz = ocpn_vis_factory.apply(dejure_ocpn)
dejure_viz_path = "evaluation/visualizations/dejure_net.png"
ocpn_vis_factory.save(dejure_gviz, dejure_viz_path)
print(f"✓ De jure net visualized: {dejure_viz_path}")
print()

# Calculate Alignments and collect statistics
print("=" * 80)
print("PROCESSING VARIANTS WITH VISUALIZATION")
print("=" * 80)

results = []
total_variants = len(filtered_ocel.variants_dict)
completed = 0
failed = 0

for variant_idx, variant_key in enumerate(tqdm(filtered_ocel.variants_dict.keys(),
                        desc="Processing variants",
                        total=total_variants,
                        unit="variant")):
    try:
        # Get variant information
        case_ids = filtered_ocel.variants_dict[variant_key]
        indirect_id = case_ids[0]  # Representative process execution
        process_execution = filtered_ocel.process_executions[indirect_id]
        num_events = len(process_execution)

        # Get variant frequency
        variant_frequency = len(case_ids)

        # Get unique objects and object types for this variant
        process_execution_objects = filtered_ocel.process_execution_objects[indirect_id]
        unique_objects = set()
        unique_object_types = set()

        # Organize objects by type
        objects_by_type = {obj_type: [] for obj_type in filtered_ocel.object_types}

        for obj_type, obj_id in process_execution_objects:
            unique_objects.add(obj_id)
            unique_object_types.add(obj_type)
            objects_by_type[obj_type].append(obj_id)

        num_objects = len(unique_objects)
        num_object_types = len(unique_object_types)

        # Extract activity sequence
        activity_sequence = [
            filtered_ocel.get_value(event_id, 'event_activity')
            for event_id in process_execution
        ]
        activity_sequence_str = ' -> '.join(activity_sequence)

        # Visualize representative process execution net
        try:
            px_net, px_ini, px_fin = process_execution_net_from_process_execution(
                filtered_ocel,
                indirect_id,
                process_execution,
                date_format='%Y-%m-%d %H:%M:%S.%f'
            )

            px_gviz = ocpn_vis_factory.apply(px_net)
            viz_filename = f"variant_{variant_idx:03d}_case_{indirect_id}.png"
            viz_path = f"evaluation/visualizations/{viz_filename}"
            ocpn_vis_factory.save(px_gviz, viz_path)
            visualization_path = viz_path
        except Exception as viz_error:
            tqdm.write(f"  ⚠ Visualization failed for variant {variant_idx}: {str(viz_error)}")
            visualization_path = "ERROR"

        # Start timing and memory tracking
        tracemalloc.start()
        start_time = timeit.default_timer()

        # Calculate alignment
        alignment = calculate_oc_alignment_given_variant_id(
            filtered_ocel,
            dejure_ocpn,
            variant_key,
            date_format='%Y-%m-%d %H:%M:%S.%f'
        )

        # Calculate execution time and memory usage
        execution_time = timeit.default_timer() - start_time
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        current_memory_mb = current_memory / 1024 / 1024
        peak_memory_mb = peak_memory / 1024 / 1024

        # Analyze moves with detailed sequence
        num_log_moves = 0
        num_model_moves = 0
        num_sync_moves = 0
        num_silent_moves = 0
        move_sequence_lines = []

        for move in alignment.moves:
            # Determine move type and collect stats
            if isinstance(move, LogMove):
                num_log_moves += 1
                move_type = "LOG"
                log_activity = move.log_move if move.log_move else "-"
                model_activity = "-"
            elif isinstance(move, DefinedModelMove):
                num_model_moves += 1
                move_type = "MODEL"
                log_activity = "-"
                model_activity = move.model_move if move.model_move else "-"
                # Check if it's a silent move
                if hasattr(move, 'silent') and move.silent:
                    num_silent_moves += 1
                    move_type = "MODEL(SILENT)"
            elif isinstance(move, SynchronousMove):
                num_sync_moves += 1
                move_type = "SYNC"
                log_activity = move.log_move if move.log_move else "-"
                model_activity = move.model_move if move.model_move else "-"
            else:
                # Catch any other move types
                move_type = f"UNKNOWN({type(move).__name__})"
                log_activity = "-"
                model_activity = "-"

            # Format: "Log: X | Model: Y | Move Type: Z | Cost: C"
            move_line = (f"Log: {log_activity} | Model: {model_activity} | "
                        f"Move Type: {move_type} | Cost: {move.cost:.3f}")
            move_sequence_lines.append(move_line)

        move_sequence_str = "\n".join(move_sequence_lines)

        # Store result with enhanced information
        result = {
            'variant_id': variant_key,
            'variant_index': variant_idx,
            'case_ids': '|'.join(map(str, case_ids)),
            'representative_exec_id': indirect_id,
            'variant_frequency': variant_frequency,
            'num_events': num_events,
            'num_objects': num_objects,
            'num_object_types': num_object_types,
            'activity_sequence': activity_sequence_str,
            'event_ids': ','.join(map(str, process_execution)),
        }

        # Add object type specific columns
        for obj_type in filtered_ocel.object_types:
            result[f'{obj_type}_objects'] = '|'.join(objects_by_type[obj_type])
            result[f'{obj_type}_count'] = len(objects_by_type[obj_type])

        # Add alignment results
        result.update({
            'alignment_cost': alignment.get_cost(),
            'num_log_moves': num_log_moves,
            'num_model_moves': num_model_moves,
            'num_sync_moves': num_sync_moves,
            'num_silent_moves': num_silent_moves,
            'total_moves': len(alignment.moves),
            'move_sequence': move_sequence_str,
            'execution_time': execution_time,
            'current_memory_mb': current_memory_mb,
            'peak_memory_mb': peak_memory_mb,
            'visualization_path': visualization_path
        })

        results.append(result)
        completed += 1

    except Exception as e:
        failed += 1
        tqdm.write(f"✗ Failed variant {variant_key}: {str(e)}")

        # Try to get basic info even on failure
        try:
            case_ids = filtered_ocel.variants_dict[variant_key]
            case_ids_str = '|'.join(map(str, case_ids))
            indirect_id = case_ids[0]
        except:
            case_ids_str = "ERROR"
            indirect_id = -1

        # Store failed result with error info
        failed_result = {
            'variant_id': variant_key,
            'variant_index': variant_idx,
            'case_ids': case_ids_str,
            'representative_exec_id': indirect_id,
            'variant_frequency': -1,
            'num_events': -1,
            'num_objects': -1,
            'num_object_types': -1,
            'activity_sequence': "ERROR",
            'event_ids': "ERROR",
        }

        # Add error placeholders for object types
        for obj_type in filtered_ocel.object_types:
            failed_result[f'{obj_type}_objects'] = "ERROR"
            failed_result[f'{obj_type}_count'] = -1

        failed_result.update({
            'alignment_cost': -1,
            'num_log_moves': -1,
            'num_model_moves': -1,
            'num_sync_moves': -1,
            'num_silent_moves': -1,
            'total_moves': -1,
            'move_sequence': f"ERROR: {str(e)}",
            'execution_time': -1,
            'current_memory_mb': -1,
            'peak_memory_mb': -1,
            'visualization_path': "ERROR"
        })

        results.append(failed_result)

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

# Save to CSV in evaluation folder
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_filename = f"evaluation/alignment_evaluation_viz_{timestamp}.csv"
df.to_csv(output_filename, index=False)
print(f"✓ Results saved to: {output_filename}")
print()

# Print statistics (only for successful alignments)
successful_df = df[df['alignment_cost'] >= 0]

if len(successful_df) > 0:
    print("Statistical Summary (successful alignments):")
    print("-" * 80)
    print(successful_df[['variant_frequency', 'num_events', 'num_objects', 'num_object_types',
                         'alignment_cost', 'num_log_moves', 'num_model_moves', 'num_sync_moves',
                         'num_silent_moves', 'execution_time', 'peak_memory_mb']].describe())
    print()

    print("Top 5 most costly alignments:")
    print("-" * 80)
    print(successful_df.nlargest(5, 'alignment_cost')[['variant_index', 'variant_frequency',
                                                         'num_events', 'num_objects',
                                                         'alignment_cost', 'execution_time',
                                                         'visualization_path']])
    print()

    print("Top 5 longest execution times:")
    print("-" * 80)
    print(successful_df.nlargest(5, 'execution_time')[['variant_index', 'num_events',
                                                         'num_objects', 'alignment_cost',
                                                         'execution_time', 'peak_memory_mb']])
    print()

    print("Top 5 highest memory usage:")
    print("-" * 80)
    print(successful_df.nlargest(5, 'peak_memory_mb')[['variant_index', 'num_events',
                                                         'num_objects', 'peak_memory_mb',
                                                         'execution_time']])
    print()

    print("Sample variant details:")
    print("-" * 80)
    sample_cols = ['variant_index', 'representative_exec_id', 'activity_sequence',
                   'application_objects', 'offer_objects', 'visualization_path']
    available_cols = [col for col in sample_cols if col in successful_df.columns]
    print(successful_df[available_cols].head())

print()
print("=" * 80)
print(f"Evaluation complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Visualizations saved to: evaluation/visualizations/")
print("=" * 80)
