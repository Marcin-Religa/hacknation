#!/usr/bin/env python3
"""Merge synthetic.jsonl with auto-labeled data (if available) and split into train/val/test.
- Expects synthetic.jsonl in the current directory.
- If auto_labels.jsonl exists, it will be included; otherwise falls back to synthetic only.
Output: train.jsonl, val.jsonl, test.jsonl (80/10/10 split).
"""
import json
import random
from pathlib import Path

random.seed(42)

SYN_PATH = Path("synthetic.jsonl")
AUTO_PATH = Path("auto_labels.jsonl")  # adjust if your auto labels are under a different name

# Canonicalize labels to contest spec, drop noisy ones
ALIAS_MAP = {
    "id-number": "document-number",
    "id_number": "document-number",
    "name-1": "name",
    "surname-1": "surname",
}

DROP_LABELS = {
    "model",
    "time",
    "subject",
    "genre",
    "programming-language",
    "version",
    "healthcare-professional",
}


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save_jsonl(path: Path, data):
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in data))


def normalize_label(label: str):
    if not label:
        return None
    norm = label.strip().lower().replace("_", "-")
    norm = ALIAS_MAP.get(norm, norm)
    if norm in DROP_LABELS:
        return None
    return norm


def normalize_entities(example):
    entities = example.get("entities", []) or []
    cleaned = []
    for ent in entities:
        if isinstance(ent, dict):
            start, end, label = ent.get("start"), ent.get("end"), ent.get("label")
        else:
            # assume tuple/list [start, end, label]
            if len(ent) < 3:
                continue
            start, end, label = ent[0], ent[1], ent[2]
        norm_label = normalize_label(label)
        if norm_label is None:
            continue
        if start is None or end is None:
            continue
        cleaned.append({"start": start, "end": end, "label": norm_label})
    example["entities"] = cleaned
    return example


def main():
    if not SYN_PATH.exists():
        raise FileNotFoundError(f"Brak pliku {SYN_PATH}")

    synthetic = load_jsonl(SYN_PATH)
    sources = [synthetic]
    if AUTO_PATH.exists():
        auto = load_jsonl(AUTO_PATH)
        sources.append(auto)
        print(f"Wczytano auto-labeled: {len(auto)} przykładów")
    else:
        print("Brak auto_labels.jsonl - używam tylko synthetic.jsonl")

    all_data = [item for src in sources for item in src]

    # Normalize labels, drop noisy ones, remove empty examples
    total_before = 0
    dropped_entities = 0
    dropped_examples = 0
    normalized = []
    for item in all_data:
        before = len(item.get("entities", []))
        total_before += before
        item = normalize_entities(item)
        after = len(item.get("entities", []))
        dropped_entities += before - after
        if after == 0:
            dropped_examples += 1
            continue
        normalized.append(item)

    all_data = normalized
    if dropped_entities or dropped_examples:
        print(
            f"Normalizacja etykiet: usunięto {dropped_entities} encji, odrzucono {dropped_examples} przykładów bez etykiet"
        )

    random.shuffle(all_data)

    n = len(all_data)
    n_train = int(0.8 * n)
    n_val = int(0.1 * n)

    train = all_data[:n_train]
    val = all_data[n_train:n_train + n_val]
    test = all_data[n_train + n_val:]

    save_jsonl(Path("train.jsonl"), train)
    save_jsonl(Path("val.jsonl"), val)
    save_jsonl(Path("test.jsonl"), test)

    print(f"train={len(train)}, val={len(val)}, test={len(test)}, total={n}")


if __name__ == "__main__":
    main()
