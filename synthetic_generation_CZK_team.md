# Synthetic Generation – CZK team

## Mechanizm
- Templaty domenowe (urzad/med/czat/wyciek/praca/szkola/dialog/ogloszenie/formal/paragraf) + domena `rare` do podbicia klas rzadkich.
- Placeholdery {name}, {surname}, {city}, {address}, {phone}, {email}, {pesel}, {bank_account}, {document_number}, {health}, {religion}, {political}, {relative}, {job_title}, {company}, {age}, {sex}, {ethnicity}, {sexual_orientation}, {school_name}, {credit_card}, {username}, {secret}, {date_of_birth}, {date}.
- Generatory: PESEL z checksumą, IBAN (PL), karty, daty (YYYY/MM/DD, DD-MM-YYYY), telefony w różnych formatach, username, secret.
- Szum: drop diakrytyków, losowe literówki, OCR-like zamiany (0/O,1/l/I), wstawki znaków (#,*,/,_), sporadyczna transliteracja.
- Rare-class boost: domena `rare` dociąża klasy sexual-orientation, ethnicity, date-of-birth, date, sex, secret, school-name; RARE_BOOST=4 zwiększa sampling tej domeny.

## Fleksja
- Miasta w miejscowniku: city_loc map (np. Warszawa→Warszawie, Kraków→Krakowie).
- Nazwiska w dopełniaczu: surname_gen (suffix y/a).
- Szablony używają city_loc/surname_gen tam, gdzie potrzeba kontekstu przypadka.

## Przykłady (szablon → syntetyk)
1. Szablon: "Spotkajmy się na {address} w {city_loc}, dzwoń {phone}."  
   Przykład: "Spotkajmy się na ul. Słoneczna 12 45-789 Kraków w Krakowie, dzwoń 533-880-221."  
   Encje: address, city, phone.

2. Szablon (rare): "Profil wrażliwy: {name} {surname}, data ur. {date_of_birth}, płeć {sex}, orientacja {sexual_orientation}, etniczność {ethnicity}, szkoła {school_name}, sekret {secret}."  
   Przykład: "Profil wrażliwy: Anna Nowak, data ur. 23-04-1996, płeć kobieta, orientacja biseksualna, etniczność polska, szkoła LO nr 1 w Warszawie, sekret W9a#kLm20!"  
   Encje: name, surname, date-of-birth, sex, sexual-orientation, ethnicity, school-name, secret.

3. Szablon (wyciek): "Wyciek loginów: {username}, hasło {secret}, karta {credit_card}, adres {address}."  
   Przykład: "Wyciek loginów: kubiak_pl, hasło Rf3@1kLm2!, karta 9981-2033-4455-6677, adres ul. Lipowa 22/5 81-221 Gdańsk."  
   Encje: username, secret, credit-card-number, address.

## Replikacja
- Generacja: `python synthetic_gen.py --count 10000` (append opcjonalny).
- Po generacji: auto-label z orig/anonymized → merge_and_split → train/val/test.

## Dbałość o sens
- Placeholdery w zdaniach odzwierciedlają realne konteksty (urzędowe/medyczne/czat). Szum celowo obniża czystość, by poprawić odporność modelu.
- Domena `rare` zapewnia, że rzadkie etykiety występują w naturalnych, spójnych zdaniach zamiast losowych wstawek.
