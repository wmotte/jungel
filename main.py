#!/usr/bin/env python3

"""
Hoofdscript voor de Jüngel preek-generator.
Implementeert iteratieve prompt-optimalisatie.
Prompts evolueren dynamisch en worden opgeslagen voor hergebruik.
"""
import asyncio
import json
import os
import glob
from datetime import datetime
from pathlib import Path

from config import MAX_ITERATIONS
from generator import generate_with_iteration, GeneratedSermon
from scorer import compute_full_score
from prompt_store import (
    get_current_best,
    get_prompt_stats,
    load_prompt_history,
    PROMPTS_DIR,
)


# Paths
OUTPUT_DIR = Path(__file__).parent / "output"
SERMONS_PATH = Path(__file__).parent / "vertaling_Wim" / "export"


def load_sermons() -> list[dict]:
    """Laad preken uit JSON bestanden."""
    sermons = []
    for file_path in glob.glob(str(SERMONS_PATH / "p*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            sermons.append(json.load(f))
    return sermons


def show_prompt_stats():
    """Toon statistieken over prompt-evolutie."""
    stats = get_prompt_stats()

    print("\n--- Prompt Evolutie Status ---")
    if stats["total_versions"] == 0:
        print("Geen opgeslagen prompts. Start met het basis prompt.")
    else:
        print(f"Totaal versies: {stats['total_versions']}")
        print(f"Beste score: {stats['best_score']:.2f}")
        print(f"Gemiddelde score: {stats['avg_score']:.2f}")
        print(f"Laatste versie: v{stats['latest_version']}")
        if stats.get('score_improvement'):
            print(f"Score verbetering (v1 -> laatste): {stats['score_improvement']:+.2f}")
    print()


def show_current_best_prompt():
    """Toon het huidige beste prompt."""
    best = get_current_best()

    if not best:
        print("\nGeen opgeslagen prompts gevonden.")
        print("Het basis prompt wordt gebruikt bij de eerste run.")
        return

    print(f"\n{'='*60}")
    print(f"HUIDIGE BESTE PROMPT (v{best.version})")
    print(f"{'='*60}")
    print(f"Score: {best.score:.2f}")
    print(f"Opgeslagen: {best.timestamp}")
    print(f"Bijbeltekst: {best.scripture_text}")
    print(f"Iteratie: {best.iteration}")
    print(f"Tokens gebruikt: {best.tokens_used}")

    if best.improvements:
        print(f"\nGeleerde verbeteringen ({len(best.improvements)}):")
        for imp in best.improvements[:5]:
            print(f"  - {imp[:80]}{'...' if len(imp) > 80 else ''}")

    print(f"\n--- PROMPT INHOUD ---")
    # Toon eerste 2000 karakters
    prompt_preview = best.system_prompt[:2000]
    print(prompt_preview)
    if len(best.system_prompt) > 2000:
        print(f"\n... [{len(best.system_prompt) - 2000} karakters weggelaten] ...")

    print(f"\n{'='*60}")


def show_prompt_history():
    """Toon de volledige prompt geschiedenis."""
    history = load_prompt_history()

    if not history:
        print("\nGeen prompt geschiedenis gevonden.")
        return

    print(f"\n{'='*60}")
    print("PROMPT GESCHIEDENIS")
    print(f"{'='*60}")

    for entry in history:
        version = entry.get("version", "?")
        score = entry.get("score", 0)
        timestamp = entry.get("timestamp", "?")[:19]
        scripture = entry.get("scripture_text", "?")[:30]
        parent = entry.get("parent_version")
        improvements = entry.get("improvements", [])

        parent_str = f" (parent: v{parent})" if parent else ""
        imp_str = f" [{len(improvements)} verbeteringen]" if improvements else ""

        print(f"v{version}: score={score:.2f} | {timestamp} | {scripture}...{parent_str}{imp_str}")

    print(f"\n{'='*60}")


async def generate_for_scripture(
    scripture_text: str,
    scripture_context: str,
    reference_sermons: list[dict],
    verbose: bool = True,
) -> GeneratedSermon:
    """Genereer een preek voor een gegeven Bijbeltekst."""
    # Extraheer teksten van training preken als referentie
    reference_texts = [s["tekst"] for s in reference_sermons]

    result = await generate_with_iteration(
        scripture_text=scripture_text,
        scripture_context=scripture_context,
        reference_sermons=reference_texts,
        max_iterations=MAX_ITERATIONS,
        target_score=0.85,
        verbose=verbose,
    )

    return result


async def single_generation_demo(
    reference_sermons: list[dict],
    #scripture_text: str = "Johannes 3:16",
    #scripture_context: str = "Want God had de wereld zo lief dat hij zijn enige Zoon heeft gegeven, opdat iedereen die in hem gelooft niet verloren gaat, maar eeuwig leven heeft.",
    scripture_text: str = "Jakobus 5:13-18",
    scripture_context: str = "Als een van u het moeilijk heeft, laat hij bidden; is hij vrolijk, laat hij een loflied zingen. Laat iemand die ziek is de oudsten van de gemeente bij zich roepen; laten ze voor hem bidden en hem met olie zalven in de naam van de Heer. Het gelovige gebed zal de zieke redden, en de Heer zal hem laten opstaan. Wanneer hij gezondigd heeft, zal het hem vergeven worden. Daarom: beken elkaar uw zonden en bid voor elkaar, dan zult u genezen. Want het gebed van een rechtvaardige is krachtig en mist zijn uitwerking niet. Elia was een mens als wij, en nadat hij vurig had gebeden dat het niet zou regenen, is er drieënhalf jaar lang geen regen gevallen op het land. Toen bad hij opnieuw, en de hemel gaf regen, en het land bracht zijn vrucht weer voort.",

) -> None:
    """Demo: genereer een enkele preek."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print(f"\n{'='*60}")
    print(f"DEMO: Preek genereren voor {scripture_text}")
    print(f"{'='*60}")

    result = await generate_for_scripture(
        scripture_text=scripture_text,
        scripture_context=scripture_context,
        reference_sermons=reference_sermons,
        verbose=True,
    )

    print(f"\n{'='*60}")
    print("GEGENEREERDE PREEK:")
    print(f"{'='*60}")
    print(result.text)
    print(f"\n{'='*60}")
    print(f"Finale score: {result.score.overall_score:.2f}")
    print(f"Iteraties: {result.iteration}")
    print(f"Prompt versie: v{result.prompt_version}")
    print(f"Tokens gebruikt: {result.input_tokens} input, {result.output_tokens} output")

    # Sla finale preek op
    output_path = OUTPUT_DIR / f"demo_{timestamp}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Bijbeltekst: {scripture_text}\n")
        f.write(f"Context: {scripture_context}\n")
        f.write(f"Prompt versie: v{result.prompt_version}\n")
        f.write(f"Score: {result.score.overall_score:.2f}\n")
        f.write(f"Iteraties: {result.iteration}\n")
        f.write(f"\n{'='*60}\n\n")
        f.write(result.text)
    print(f"\nFinale preek opgeslagen: {output_path}")

    # Sla ook het gebruikte prompt op
    prompt_path = OUTPUT_DIR / f"demo_{timestamp}_prompt.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(result.final_prompt)
    print(f"Prompt opgeslagen: {prompt_path}")


async def main():
    """Hoofdfunctie."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Jüngel Preek Generator")
    print("=" * 60)

    # Toon prompt statistieken
    show_prompt_stats()

    # Laad data
    print("Data laden...")
    sermons = load_sermons()
    print(f"Totaal {len(sermons)} preken geladen als referentie.")


    # Menu
    print("\nKies een optie:")
    print("1. Demo: genereer een enkele preek")
    print("2. Genereer preek voor eigen Bijbeltekst")
    print("3. Bekijk huidige beste prompt")
    print("4. Bekijk prompt geschiedenis")

    choice = input("\nKeuze (1/2/3/4): ").strip()

    if choice == "1":
        await single_generation_demo(sermons)

    elif choice == "2":
        scripture = input("Bijbeltekst (bijv. 'Matteüs 5:9'): ").strip()

        print("\nHoe wil je de tekst invoeren?")
        print("  1. Plakken (typ 'END' op een nieuwe regel om te eindigen)")
        print("  2. Uit bestand laden")
        input_method = input("Keuze (1/2): ").strip()

        if input_method == "2":
            file_path = input("Pad naar tekstbestand: ").strip()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context = f.read().strip()
                print(f"Tekst geladen ({len(context)} karakters)")
            except FileNotFoundError:
                print(f"Bestand niet gevonden: {file_path}")
                return
        else:
            print("Plak de bijbeltekst (typ 'END' op een nieuwe regel om te eindigen):")
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == "END":
                        break
                    lines.append(line)
                except EOFError:
                    break
            context = " ".join(lines).strip()

        if not context:
            print("Geen tekst ingevoerd.")
            return

        result = await generate_for_scripture(
            scripture_text=scripture,
            scripture_context=context,
            reference_sermons=sermons,
            verbose=True,
        )

        print(f"\n{'='*60}")
        print("GEGENEREERDE PREEK:")
        print(f"{'='*60}")
        print(result.text)

        # Sla preek en prompt op
        output_path = OUTPUT_DIR / f"sermon_{timestamp}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Bijbeltekst: {scripture}\n")
            f.write(f"Prompt versie: v{result.prompt_version}\n")
            f.write(f"Score: {result.score.overall_score:.2f}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(result.text)
        print(f"\nPreek opgeslagen in: {output_path}")

        # Sla ook het gebruikte prompt op
        prompt_output = OUTPUT_DIR / f"sermon_{timestamp}_prompt.txt"
        with open(prompt_output, "w", encoding="utf-8") as f:
            f.write(f"Prompt versie: v{result.prompt_version}\n")
            f.write(f"Score: {result.score.overall_score:.2f}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(result.final_prompt)
        print(f"Prompt opgeslagen in: {prompt_output}")

    elif choice == "3":
        show_current_best_prompt()

    elif choice == "4":
        show_prompt_history()

    else:
        print("Ongeldige keuze")


if __name__ == "__main__":
    asyncio.run(main())
