
import glob
import json
import re
from collections import defaultdict
import os

def find_duplicate_citations():
    """
    Finds all 'mogelijk*.json' files and reports any duplicate citations
    found across the files.
    """
    files = glob.glob('docs/mogelijk_*.json')
    # Data structure: {'Author': {'Quote': [file1, file2, ...]}}
    citations = defaultdict(lambda: defaultdict(list))

    pattern = re.compile(r"([\w\s\.]+)[\- ](?:citaat|referentie) toegevoegd(?:\s*(.*?))?", re.IGNORECASE)

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes = data.get('_wijzigingen', [])
            file_name = os.path.basename(file_path)

            for change in changes:
                if "Heidegger en Rudolf Otto referenties behouden" in change:
                    citations["Heidegger"]["Referentie (geen specifieke quote in log)"].append(file_name)
                    citations["Rudolf Otto"]["Referentie (geen specifieke quote in log)"].append(file_name)
                    continue

                match = pattern.search(change)
                if match:
                    author = match.group(1).strip()
                    quote = match.group(2)
                    
                    author = ' '.join(word.capitalize() for word in author.split())

                    if author.lower() in ["haben→zijn", "expliciete hebben→sein terminologie"]:
                        continue
                    
                    if quote:
                        citations[author][quote.strip()].append(file_name)

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error processing {file_path}: {e}")

    duplicates_found = False
    print("Controleren op dubbele citaten in 'mogelijke preken'...\n")
    
    for author, quotes_data in sorted(citations.items()):
        for quote, file_list in quotes_data.items():
            if len(file_list) > 1:
                if not duplicates_found:
                    print("De volgende dubbele citaten/referenties zijn gevonden:\n")
                    duplicates_found = True
                print(f"--- Citaat/referentie van {author} (gevonden in {len(file_list)} bestanden) ---")
                print(f"  Tekst: \"{quote}\"")
                print(f"  Bestanden: {', '.join(sorted(file_list))}")
                print()

    if not duplicates_found:
        print("Er zijn geen dubbele citaten gevonden.")

if __name__ == "__main__":
    find_duplicate_citations()
