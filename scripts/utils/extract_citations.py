import glob
import json
import re
from collections import defaultdict

def extract_unique_citations():
    """
    Finds all 'mogelijk*.json' files, extracts author citations from the
    '_wijzigingen' field, and prints a unique list.
    Corrected to handle Unicode characters in names.
    """
    files = glob.glob('docs/mogelijk_*.json')
    citations = defaultdict(set)

    # Regex to capture author and optional quote from the '_wijzigingen' field.
    # Now handles Unicode characters and is case-insensitive.
    pattern = re.compile(r"([\w\s\.]+)[\- ](?:citaat|referentie) toegevoegd(?:\s*\((.*?)\))?", re.IGNORECASE)

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes = data.get('_wijzigingen', [])
            for change in changes:
                # Special case for Heidegger/Otto from mogelijk_06_nl.json which is not in ()
                if "Heidegger en Rudolf Otto referenties behouden" in change:
                    citations["Heidegger"].add("Referentie (geen specifieke quote in log)")
                    citations["Rudolf Otto"].add("Referentie (geen specifieke quote in log)")
                    continue

                match = pattern.search(change)
                if match:
                    author = match.group(1).strip()
                    quote = match.group(2)
                    
                    # Capitalize author name for consistency
                    author = ' '.join(word.capitalize() for word in author.split())

                    # Skip known non-author patterns
                    if author.lower() in ["haben→zijn", "expliciete hebben→sein terminologie"]:
                        continue
                    
                    if quote:
                        citations[author].add(quote.strip())

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error processing {file_path}: {e}")

    if not citations:
        print("Geen citaten gevonden in de opgegeven bestanden.")
        return

    print("Unieke citaten en referenties gevonden in de 'mogelijke preken' (gecorrigeerde versie):\n")
    for author, quotes in sorted(citations.items()):
        print(f"--- {author} ---")
        if quotes:
            for i, quote in enumerate(sorted(list(quotes)), 1):
                print(f"  {i}. {quote}")
        print()

if __name__ == "__main__":
    extract_unique_citations()