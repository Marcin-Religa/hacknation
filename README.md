# CZK team – Hybrid Regex + HerBERT NER (offline)

## What this is
Offline anonymization pipeline for Polish PII. Hybrid: deterministic regex validators for hard identifiers (PESEL/email/phone/IBAN/document) plus finetuned token-classification (allegro/herbert-base-cased) for contextual entities (name, surname, city/address, relative, health, etc.).

## Repository map
- [synthetic_gen.py](synthetic_gen.py): templated synthetic data generator (includes rare-class boost domain).
- [auto_label_from_orig.py](auto_label_from_orig.py): aligns info/orig.txt vs info/anonymized.txt to spans (start, end, label) with alias/drop normalization.
- [merge_and_split.py](merge_and_split.py): merge synthetic + auto labels, normalize labels, drop noise, split 80/10/10 → train/val/test.
- [train_ner.py](train_ner.py): finetuning token classification (span→BIO on the fly).
- [evaluate_hybrid.py](evaluate_hybrid.py): evaluation helper (model + regex if enabled).
- [inference.py](inference.py): end-to-end anonymization (regex pre-mask + model + postprocess).
- [outputs/](outputs/): place model checkpoints (e.g., outputs/herbert-ner-local/).
- Data splits: [train.jsonl](train.jsonl), [val.jsonl](val.jsonl), [test.jsonl](test.jsonl) (span format: text + entities[{start,end,label}]).
- Submission helper files (to fill): performance_CZK_team.txt, preprocessing_CZK_team.md, synthetic_generation_CZK_team.md, output_CZK_team.txt (overwrite with organizer test output), presentation_CZK_team.pdf (add manually).

## Installation (local CPU/GPU)
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
(Optional) spaCy small PL model for POS/tokenization:
```bash
python -m spacy download pl_core_news_sm
```

## Regenerate data (optional)
```bash
python synthetic_gen.py --count 10000
.venv/bin/python auto_label_from_orig.py
.venv/bin/python merge_and_split.py
```

## Training (example; adjust batch for your GPU)
```bash
.venv/bin/python train_ner.py \
  --train train.jsonl \
  --val val.jsonl \
  --output outputs/herbert-ner-local \
  --epochs 3 \
  --batch 8 \
  --lr 5e-5
```
If VRAM is low, reduce `--batch` or run on CPU (slower). Model checkpoint goes to outputs/herbert-ner-local/.

## Inference (produce submission output)
Assuming checkpoint in outputs/herbert-ner-local/ and input file input.txt from organizer:
```bash
.venv/bin/python inference.py \
  --model outputs/herbert-ner-local \
  --input input.txt \
  --output output_CZK_team.txt
```
- Keeps line order 1:1 with input.
- Uses regex validators for PESEL/email/phone/IBAN/document, then contextual NER.

## Evaluation
Micro F1 on test split (local model ~0.99 F1 when trained locally):
```bash
.venv/bin/python evaluate_hybrid.py \
  --model outputs/herbert-ner-local \
  --test test.jsonl
```

## Submission checklist (ChallengeRocket)
- README.md (this file).
- output_CZK_team.txt (must be generated on organizer test input; overwrite placeholder).
- performance_CZK_team.txt (fill time/hardware/API info after timing inference; exclude model load time).
- preprocessing_CZK_team.md (included; describes auto-label + split).
- synthetic_generation_CZK_team.md (included; describes templates/rare boost/examples).
- presentation_CZK_team.pdf (add manually, max 5 slides).

## Hardware
- Local run on Apple M1

## Notes
- Labels normalized to contest spec (25 classes); aliases (id-number→document-number, name-1→name, surname-1→surname); dropped noisy labels (model/time/subject/genre/programming-language/version/healthcare-professional).
- Synthetic generator has rare-class domain to upsample minority labels (sexual-orientation, ethnicity, date-of-birth, date, sex, secret, school-name).
- Inference is fully offline (no external APIs).
