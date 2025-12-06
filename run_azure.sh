#!/bin/bash
set -e

# Default settings
COUNT=100000
EPOCHS=10
BATCH=16
MODEL="allegro/herbert-large-cased"
OUTPUT_DIR="outputs/ner_large"

# Allow overrides
DEVICE="cuda"
EXTRA_ARGS=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) COUNT=50; EPOCHS=1; BATCH=2; MODEL="allegro/herbert-base-cased"; OUTPUT_DIR="outputs/dry_run"; DEVICE="cpu"; EXTRA_ARGS="--no_mps"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

echo ">>> Activating environment..."
source .venv/bin/activate

echo ">>> Generating synthetic data ($COUNT examples)..."
python synthetic_gen.py --count $COUNT

echo ">>> Auto-labeling data..."
python auto_label_from_orig.py

echo ">>> Merging and splitting datasets..."
python merge_and_split.py

echo ">>> Starting training ($MODEL, Epochs: $EPOCHS, Batch: $BATCH)..."
# Ensure clean start
rm -rf $OUTPUT_DIR
python train_ner.py \
    --train train.jsonl \
    --val val.jsonl \
    --model $MODEL \
    --output $OUTPUT_DIR \
    --epochs $EPOCHS \
    --batch $BATCH \
    --lr 2e-5 \
    $EXTRA_ARGS

echo ">>> Evaluation..."
python evaluate_hybrid.py --model $OUTPUT_DIR --data test.jsonl --device $DEVICE

echo ">>> Done! Artifacts in $OUTPUT_DIR"
