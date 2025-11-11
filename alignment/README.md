# Weighted Object-Centric Alignment Testing

This directory contains a comprehensive test suite for the new weighted alignment functionality.

## Overview

The weighted alignment feature allows you to assign different importance levels (weights) to different activities when calculating object-centric alignments. This enables more nuanced conformance checking where deviations in critical activities are penalized more heavily than deviations in less important activities.

## Directory Structure

```
alignment/
├── data/
│   ├── order_process.jsonocel           # Full event log for OCPN discovery
│   ├── single_trace.jsonocel            # Single trace for alignment testing
│   ├── activity_weights.json            # Equal weights for all activities
│   └── activity_weights_varied.json     # Varied weights by importance
├── weighted_alignment_test.ipynb        # Main test notebook
└── README.md                            # This file
```

## Data Files

### order_process.jsonocel
- **Purpose**: Full event log used to discover the OCPN (reference model)
- **Content**: Complete order processing event log with multiple traces
- **Usage**: Input for OCPN discovery algorithm

### single_trace.jsonocel
- **Purpose**: Single process execution for alignment calculation
- **Content**: First 10 events from the full log
- **Usage**: Compared against OCPN to compute alignment

### activity_weights.json
- **Purpose**: Equal weight distribution (baseline for testing)
- **Format**: `{"Activity Name": 0.0909, ...}`
- **Note**: All weights sum to 1.0

### activity_weights_varied.json
- **Purpose**: Importance-based weight distribution
- **Format**: `{"Activity Name": weight, ...}`
- **Distribution**:
  - `Place Order`: 0.25 (most important)
  - `Confirm Order`: 0.20
  - `Pick Item`: 0.15
  - `Pay Order`: 0.12
  - `Start Route`: 0.10
  - `Load Cargo`: 0.08
  - `End Route`: 0.05
  - Other activities: 0.0-0.03

## Jupyter Notebook

### weighted_alignment_test.ipynb

The notebook is organized into 5 parts:

#### Part 1: Data Loading
- Load full OCEL for OCPN discovery
- Discover OCPN from full log
- Load single trace OCEL for alignment
- Load activity weights (equal and varied)

#### Part 2: Standard Alignment (Baseline)
- Calculate alignment using original `calculate_oc_alignments()`
- Visualize alignment
- Record baseline cost for comparison
- **Formula**: `cost = len(objects)`

#### Part 3: Weighted Alignment with Zero Weights
- Test weighted alignment with all weights = 0
- Should produce identical results to Part 2
- Validates correctness of implementation
- **Formula**: `cost = len(objects) * (1 + 0) = len(objects)`

#### Part 4: Weighted Alignment with Varied Weights
- Apply importance-based weights
- Compare costs with baseline
- Show move-by-move cost differences
- **Formula**: `cost = len(objects) * (1 + weight)`
- **Example**: Activity with weight=0.25 and 2 objects → cost = 2 × 1.25 = 2.5

#### Part 5: Custom Formula Alignment
- Use custom cost formula: `cost = len(objects) * (1 + weight * 100)`
- Demonstrates flexibility of cost function approach
- Amplifies weight effect by 100x
- **Example**: Activity with weight=0.25 and 2 objects → cost = 2 × 26 = 52

## Running the Notebook

### Prerequisites

```bash
# Install required dependencies
pip install pm4py pandas matplotlib jupyter
```

### Execution

```bash
cd alignment
jupyter notebook weighted_alignment_test.ipynb
```

Or run all cells programmatically:

```bash
jupyter nbconvert --to notebook --execute weighted_alignment_test.ipynb
```

## Expected Results

### Cost Comparison

For the sample data, you should see:

1. **Standard alignment**: Baseline cost (e.g., 10.0)
2. **Zero-weight alignment**: Identical to standard (10.0)
3. **Varied-weight alignment**: Higher cost (e.g., 12.5)
4. **Custom formula alignment**: Much higher cost (e.g., 250.0)

### Validation Checks

- ✓ Zero-weight cost should match standard cost (within 0.001)
- ✓ Number of moves should be identical across all methods
- ✓ Only move costs should differ, not move sequences
- ✓ Synchronous moves should always have cost = 0
- ✓ Silent transitions should always have cost = 0.001

## Use Cases

### 1. Compliance-Critical Activities

Assign higher weights to compliance-critical activities:

```json
{
  "Authorization Check": 0.4,
  "Approval": 0.3,
  "Documentation": 0.2,
  "Other activities": 0.1
}
```

### 2. Time-Sensitive Processes

Penalize deviations in time-critical activities:

```json
{
  "Emergency Response": 0.5,
  "Urgent Order": 0.3,
  "Standard Order": 0.2
}
```

### 3. Cost-Based Weighting

Weight activities by their operational cost:

```json
{
  "Expensive Operation": 0.4,
  "Moderate Operation": 0.3,
  "Cheap Operation": 0.3
}
```

## API Usage

### Simple Usage

```python
from ocpa.algo.conformance.alignments import algorithm as alignment_factory

# Define weights
weights = {
    "Place Order": 0.3,
    "Confirm Order": 0.5,
    "Ship Order": 0.2
}

# Calculate weighted alignment
alignments = alignment_factory.calculate_oc_alignments_with_weights(
    ocel, ocpn, weights
)
```

### Advanced Usage with Custom Formula

```python
from ocpa.algo.conformance.alignments.alignment import create_custom_cost_function

# Define custom formula
formula = lambda num_obj, weight: (num_obj ** 2) * (1 + weight)

# Create cost function
cost_fn_creator = create_custom_cost_function(formula)
cost_fn = cost_fn_creator(weights)

# Calculate alignment
alignments = alignment_factory.calculate_oc_alignments_with_cost_function(
    ocel, ocpn, cost_fn
)
```

## Visualization

The notebook uses `alignment_viz()` from `ocpa.visualization.alignment_viz.visualization` to create visual representations of alignments. Each visualization shows:

- **Move boxes**: Activity and object information
- **Line styles**:
  - Solid line: Synchronous move (perfect match)
  - Dashed line: Model move (expected but not occurred)
  - Dash-dot line: Log move (occurred but not expected)
- **Object colors**: Different colors for different object instances
- **Cost**: Total alignment cost in title

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'jsonschema'"

```bash
pip install jsonschema
```

### Issue: "ModuleNotFoundError: No module named 'ocpa'"

Ensure PYTHONPATH includes the ocpa directory:

```python
import sys
sys.path.insert(0, '/path/to/ocpa')
```

### Issue: Alignment costs are all the same

Check that:
1. Your weights are properly loaded (not all zero)
2. Your trace actually has log moves or model moves (not all sync moves)
3. The activity names in weights match the activity names in OCEL

## References

- **Paper**: "Object-Centric Alignments" (van der Aalst et al.)
- **Implementation**: `ocpa/algo/conformance/alignments/algorithm.py`
- **Cost Functions**: `ocpa/algo/conformance/alignments/alignment.py`
- **Visualization**: `ocpa/visualization/alignment_viz/visualization.py`

## Contributing

To extend this test suite:

1. Add new data files to `data/`
2. Create new cells in the notebook
3. Document your extensions in this README
4. Submit a pull request

## License

Same as the main OCPA project.
