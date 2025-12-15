import json
import re
import glob
import os

def normalize_scripture_field(s):
    s = s.strip() # Corrected from s.trim()
    # Handle specific book name changes
    s = s.replace("Handelingen der Apostelen", "Handelingen")
    s = s.replace("Korinthe", "Korintiërs")
    s = s.replace("Mattëus", "Matteüs")
    # Remove dots from number prefixes of book names
    s = re.sub(r'^(\d+)\.\s(.+)', r'\1 \2', s)

    # Remove spaces around colon and dash
    s = re.sub(r'\s*:\s*', ':', s)
    s = re.sub(r'\s*-\s*', '-', s)
    return s

files_to_process = [
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_11_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_12_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_09_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_08_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_07_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_06_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_03_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_02_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_17_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_15_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_05_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_01_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_04_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_05_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_11_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_12_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_06_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_13_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_14_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_10_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/preek_01_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_18_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_16_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_14_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_13_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_10_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_09_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_08_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_07_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_04_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_03_nl.json",
    "/Users/wmotte/Desktop/projects/jungel/docs/paulus_02_nl.json"
]

for file_path in files_to_process:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'schriftgedeelte' in data and isinstance(data['schriftgedeelte'], str):
            original_scripture = data['schriftgedeelte']
            normalized_scripture = normalize_scripture_field(original_scripture)
            
            if original_scripture != normalized_scripture:
                data['schriftgedeelte'] = normalized_scripture
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"Normalized '{original_scripture}' to '{normalized_scripture}' in {file_path}")
            else:
                print(f"No change needed for '{original_scripture}' in {file_path}")
        else:
            print(f"Skipping {file_path}: 'schriftgedeelte' not found or not a string.")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print("Normalization complete.")