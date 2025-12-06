import json
import re
from pathlib import Path
from typing import List, Tuple, Dict

ORIG_PATH = Path("info/orig.txt")
ANON_PATH = Path("info/anonymized.txt")
OUTPUT_PATH = Path("auto_labels.jsonl")

# Map placeholder tokens to final label names (normalized to contest spec)
# Unknown labels will be normalized via lower/underscore→dash.
LABEL_NORMALIZE = {
    "phone": "phone",
    "email": "email",
    "pesel": "pesel",
    "address": "address",
    "city": "city",
    "name": "name",
    "surname": "surname",
    "bank_account": "bank-account",
    "bank-account": "bank-account",
    "document_number": "document-number",
    "document-number": "document-number",
    "company": "company",
    "school_name": "school-name",
    "job_title": "job-title",
    "relative": "relative",
    "health": "health",
    "religion": "religion",
    "political": "political-view",
    "sex": "sex",
    "ethnicity": "ethnicity",
    "sexual_orientation": "sexual-orientation",
    "secret": "secret",
    "username": "username",
    "credit_card": "credit-card-number",
    "credit-card": "credit-card-number",
    "date": "date",
    "date_of_birth": "date-of-birth",
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


def normalize_label(raw: str) -> str:
    key = raw.strip().strip("[]")
    key = key.replace(" ", "_").replace("-", "-").replace("/", "_")
    key = key.lower()
    key = key.replace("__", "_")
    key = key.replace("_", "-")
    key = LABEL_NORMALIZE.get(key, key)
    if key in DROP_LABELS:
        return None
    return key


def find_entities(orig: str, anon: str) -> List[Dict[str, object]]:
    """
    Align placeholders in orig with concrete spans in anon.
    Placeholders look like [label]. We capture the anon substring between
    the context before and after the placeholder.
    """
    entities: List[Dict[str, object]] = []
    i = j = 0
    length_o, length_a = len(orig), len(anon)
    while i < length_o:
        if orig[i] == "[":
            end = orig.find("]", i)
            if end == -1:
                break
            raw_label = orig[i + 1 : end]
            label = normalize_label(raw_label)
            # Literal text after this placeholder until next '[' or end
            next_bracket = orig.find("[", end + 1)
            literal_after = orig[end + 1 : next_bracket if next_bracket != -1 else length_o]
            # Build a loose pattern to find literal_after in anon
            if literal_after:
                pat = re.escape(literal_after)
                pat = pat.replace("\\ ", "\\s+")
                m = re.search(pat, anon[j:])
                if m:
                    start_a = j
                    end_a = j + m.start()
                    if end_a > start_a and label is not None:
                        entities.append({"start": start_a, "end": end_a, "label": label})
                    j = j + m.end()
                else:
                    # literal not found; take the rest of the line
                    if label is not None:
                        entities.append({"start": j, "end": length_a, "label": label})
                    j = length_a
            else:
                # Placeholder at end of line
                if label is not None:
                    entities.append({"start": j, "end": length_a, "label": label})
                j = length_a
            i = end + 1
        else:
            # Advance while characters align; if mismatch, advance anon pointer to resync
            if j < length_a and orig[i] == anon[j]:
                i += 1
                j += 1
            else:
                j += 1
                if j > length_a:
                    break
    # Deduplicate overlapping identical spans (rare)
    deduped = []
    seen = set()
    for ent in entities:
        key = (ent["start"], ent["end"], ent["label"])
        if key not in seen and ent["end"] > ent["start"]:
            deduped.append(ent)
            seen.add(key)
    return deduped


def main():
    if not ORIG_PATH.exists() or not ANON_PATH.exists():
        raise FileNotFoundError("Missing orig.txt or anonymized.txt under info/")

    with ORIG_PATH.open() as f_orig, ANON_PATH.open() as f_anon:
        orig_lines = f_orig.readlines()
        anon_lines = f_anon.readlines()

    if len(orig_lines) != len(anon_lines):
        raise ValueError("orig.txt and anonymized.txt must have the same number of lines")

    examples = []
    for idx, (orig, anon) in enumerate(zip(orig_lines, anon_lines)):
        orig = orig.rstrip("\n")
        anon = anon.rstrip("\n")
        ents = find_entities(orig, anon)
        if ents:
            examples.append({"text": anon, "entities": ents, "meta": {"source": "auto"}})

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Stats
    label_counts: Dict[str, int] = {}
    for ex in examples:
        for e in ex["entities"]:
            label_counts[e["label"]] = label_counts.get(e["label"], 0) + 1

    print(f"Zapisano {len(examples)} przykładów do {OUTPUT_PATH}")
    print("Liczność etykiet:")
    for k, v in sorted(label_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
