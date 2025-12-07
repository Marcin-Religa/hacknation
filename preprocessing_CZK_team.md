# Preprocessing – CZK team

## Auto-labeling z danych oryginalnych
- Wejście: info/orig.txt (surowe) oraz info/anonymized.txt (zanonimizowane przez organizatora).
- Skrypt: [auto_label_from_orig.py](auto_label_from_orig.py)
  - Wyrównuje linia-po-linii, wykrywa różnice jako spany (start, end, label).
  - Normalizuje etykiety do zestawu konkursowego, aliasy (id-number→document-number, name-1→name, surname-1→surname), drop etykiet spoza spec (model/time/subject/genre/programming-language/version/healthcare-professional).
  - Wynik: [auto_labels.jsonl](auto_labels.jsonl) w formacie: { "text": str, "entities": [{start, end, label}] }.

## Łączenie z danymi syntetycznymi i split
- Skrypt: [merge_and_split.py](merge_and_split.py)
  - Wejścia: synthetic.jsonl (generator), auto_labels.jsonl (auto-label).
  - Normalizacja etykiet (jak wyżej), usunięcie encji spoza spec i przykładów bez encji.
  - Shuffle, split 80/10/10 → [train.jsonl](train.jsonl), [val.jsonl](val.jsonl), [test.jsonl](test.jsonl).

## Format danych
- Każdy rekord: { "text": str, "entities": [{"start": int, "end": int, "label": str}], ... }.
- Etykiety: 25 klas konkursowych (name, surname, age, date-of-birth, date, sex, religion, political-view, ethnicity, sexual-orientation, health, relative, city, address, email, phone, pesel, document-number, company, school-name, job-title, bank-account, credit-card-number, username, secret).

## Uwagi
- Wszystkie operacje są offline, brak zewnętrznych API.
- Do regeneracji: `python synthetic_gen.py --count 10000` → `.venv/bin/python auto_label_from_orig.py` → `.venv/bin/python merge_and_split.py`.
