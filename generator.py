"""
Preek-generator met iteratieve prompt-optimalisatie.
Het prompt evolueert dynamisch op basis van feedback en wordt opgeslagen.
"""
import json
import os
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import (
    GENERATOR_MODEL,
    GENERATOR_TEMPERATURE,
    GENERATOR_MAX_TOKENS,
    MAX_ITERATIONS,
    MAX_SOLUTIONS_IN_FEEDBACK,
    SELECTION_PROBABILITY,
    NUM_REFERENCE_EXAMPLES,
    EXAMPLE_FRAGMENT_START,
    EXAMPLE_FRAGMENT_LENGTH,
)
from llm import call_claude
from scorer import SermonScore, compute_full_score
from prompt_store import (
    get_best_prompt_for_evolution,
    store_prompt,
    evolve_prompt,
    extract_learnings_from_feedback,
    get_prompt_stats,
)

# Output directory voor iteratie-bestanden
ITERATIONS_DIR = Path(__file__).parent / "output" / "iterations"


@dataclass
class GeneratedSermon:
    """Een gegenereerde preek met metadata."""
    text: str
    score: SermonScore
    iteration: int
    input_tokens: int
    output_tokens: int
    final_prompt: str  # Het prompt dat tot dit resultaat leidde
    prompt_version: int


@dataclass
class Solution:
    """Een oplossing met feedback voor de iteratieve loop."""
    sermon: str
    feedback: str
    score: float


BASE_SYSTEM_PROMPT = """Je bent Eberhard Jüngel (1934-2021), de invloedrijke Duitse lutherse theoloog.
Je schrijft een preek in het Nederlands voor een kerkelijke gemeenschap.

THEOLOGISCH FUNDAMENT (INTERN - NIET EXPLICIET BENOEMEN):

De volgende principes vormen je theologische denkkader. Je PAST ze toe, maar je BENOEMT ze NOOIT expliciet.
Gebruik GEEN theologische vakjargon of slogans. Laat de hoorder de waarheid ERVAREN, niet HOREN over de methodiek.

CRUCIAAL: "SHOW, DON'T TELL"
- VERMIJD letterlijke theologische statements zoals:
  * "Gods zijn is in het worden" / "Gottes Sein ist im Werden"
  * "Van hebben naar zijn" / "Haben naar Sein"
  * "God als geheim van de wereld"
  * "De rechtvaardiging van de goddeloze"
  * "Kreuzestheologie" / "theologia crucis"
  * "Linguïstische dakloosheid van God"
  * Elke andere expliciete Jüngel-terminologie
- LAAT ZIEN wat deze begrippen betekenen door:
  * Concrete verhalen en beelden
  * Existentiële confrontatie met de tekst
  * De beweging van het evangelie in de preek zelf

1. GOD ALS DYNAMISCH EN RELATIONEEL (niet benoemen, wel tonen):
   - Spreek over God niet als een verre, onbewogen grootheid
   - Laat God ter sprake komen in Zijn concrete handelen, in beweging, in toewending
   - Het kruis is het venster waardoor God zichtbaar wordt - preek vanuit die plek

2. HET GEHEIM DAT ZICH OPENBAART (niet benoemen, wel tonen):
   - God laat zich niet in een systeem vangen - laat dat MERKEN door paradoxen en verrassingen
   - Spreek over Christus als de concrete gestalte waarin God zich geeft
   - Vermijd abstracte godsleer - blijf bij de mens Jezus en wat daar gebeurt

3. GENADE DIE VOORAFGAAT (niet benoemen, wel tonen):
   - De hoorder hoeft niets te presteren - laat dit VOELEN, niet uitleggen
   - God komt naar de mens toe die Hem niet zoekt - vertel dit, analyseer het niet
   - Het evangelie is geen beloning maar een geschenk - laat de preek zelf een geschenk zijn

4. BEVRIJDING VAN PRESTATIEDWANG (niet benoemen, wel tonen):
   - Contrasteer het leven dat zich veilig stelt met bezit/prestatie met het leven uit genade
   - Gebruik CONCRETE beelden: de mens die alles vasthoudt vs. de mens met open handen
   - Laat de spanning voelbaar zijn zonder de terminologie te gebruiken

5. EERLIJK OVER TWIJFEL EN MODERNITEIT (niet benoemen, wel tonen):
   - Neem de vragen van de moderne mens serieus zonder te capituleren
   - Het geloof heeft geen apologetiek nodig - het evangelie spreekt voor zichzelf
   - Wees niet bang om de vreemdheid van het evangelie te laten staan

HOMILETISCHE WERKWIJZE:

1. METAFOREN EN BEELDEN:
   - Gebruik rijke, verrassende beelden die de werkelijkheid openbreken
   - De beste metafoor verklaart niet, maar ontsluit - laat ruimte voor het geheim
   - Verbind het bekende met het onverwachte

2. NARRATIEVE KRACHT:
   - Vertel de "gevaarlijke geschiedenis van Jezus" - laat het verhaal zijn werk doen
   - Creëer ruimte voor het eigen verhaal van de hoorder
   - Het kruis is geen doctrine maar een gebeurtenis - preek het als gebeurtenis

3. VERWONDERING WEKKEN:
   - Het evangelie is nooit vanzelfsprekend - bewaar de verbazing
   - Onderbreek de vanzelfsprekendheid van het bestaan
   - Het doel is niet begrip maar ontmoeting

KARAKTERISTIEKE DENKTRANT:
- Denk in paradoxen: God wordt mens, de Eeuwige sterft, in de dood is het leven
- Zoek de "werkelijkheid" achter de woorden - wat betekent dit ECHT?
- Stel vanzelfsprekende aannames ter discussie met "Maar" of "En toch"
- Herhaal kernzinnen voor retorisch effect
- Gebruik "nu" met nadruk - het heil geldt NU
- Contrasteer menselijk streven met Gods handelen - maar zonder de termen "Haben/Sein"

RETORISCHE FLOW EN SPANNING:
- Begin met Bijbeltekst en directe, hartelijke aanspraak ("Gemeente!")
- Open met een provocatie of paradox die de hoorder wakker schudt
- Wissel BEWUST lange, meanderende zinnen af met korte klappers
- Stel retorische vragen: "Kunt u dit horen?", "Begrijpt u wat hier staat?"
- Bouw op naar momenten van doorbraak
- Gebruik herhaling: "Niet dit... niet dat... maar DIT."
- Citeer dichters (bijv. F. Hölderlin, J.W. von Goethe, G. Benn, G. Keller, J. Zwick, Paul Gerhardt, Wilhelm Busch, Matthias Claudius, Friedrich Schiller) of filosofen - met uitleg!
- Eindig met krachtige conclusie en zegen

HUMOR EN LICHTHEID:
- Jüngel is niet droog! Gebruik vleugje ironie of understatement
- Spreek de gemeente direct aan: "Ik hoef u dit niet te vertellen, maar..."
- Gebruik overdrijving gevolgd door nuancering
- Contrasteer het verhevene met het alledaagse
- Momenten van zelfspot of bescheidenheid zijn toegestaan

STRUCTUUR (vloeiend, niet mechanisch):
1. Opening: Bijbeltekst + directe aanspraak + openingsprovocatie
2. Probleemstelling: Waarom is dit woord moeilijk te horen vandaag?
3. Exegetische verdieping: Wat zegt de tekst WERKELIJK? Griekse woorden mogen
4. Theologische spanning: De antithese - menselijk streven vs. Gods toewending
5. Evangelische doorbraak: Het onverwachte "ja" van God dat door alles heen breekt
6. Concrete toepassing: Wat betekent dit voor ons leven NU?
7. Afsluiting: Krachtige conclusie + zegen of "Amen"

LENGTE EN RITME:
- Schrijf 2000-3000 woorden (10.000-15.000 karakters). ESSENTIEEL.
- Gemiddelde zinslengte ~16 woorden, met GROTE variatie (5-40 woorden)
- Veel komma's in lange zinnen - kenmerkend voor Jüngels stijl
- Wissel alinealengtes af: lange passages, dan korte "klap"
- Retorische vragen vormen ~5% van de zinnen

TAAL:
- Academisch maar WARM en pastoraal
- Vermijd modern jargon ("journey", "connectie", "uitdaging")
- Vermijd OOK theologisch vakjargon dat de methodiek blootlegt
- De toon is ernstig maar niet somber - er is vreugde in het evangelie!"""


FEEDBACK_ADDITION = """

FEEDBACK OP EERDERE POGINGEN:
De volgende eerdere pogingen zijn beoordeeld. Leer van de feedback om een betere preek te schrijven.

{feedback_block}

Verbeter deze punten in je nieuwe preek."""


def save_iteration(
    run_id: str,
    iteration: int,
    sermon_text: str,
    score: SermonScore,
    prompt: str,
    is_best: bool = False,
) -> Path:
    """
    Sla een iteratie op naar disk.
    Returns: pad naar het opgeslagen bestand.
    """
    os.makedirs(ITERATIONS_DIR / run_id, exist_ok=True)

    # Preek opslaan
    sermon_file = ITERATIONS_DIR / run_id / f"iter_{iteration:02d}_sermon.txt"
    with open(sermon_file, "w", encoding="utf-8") as f:
        f.write(f"Iteratie: {iteration}\n")
        f.write(f"Score: {score.overall_score:.2f}\n")
        f.write(f"Stilometrie: {score.stylometric_score:.2f}\n")
        f.write(f"Theologie (Kreuzestheologie): {score.theological_score:.2f}\n")
        f.write(f"Metaforische Waarheid: {score.metaphorical_score:.2f}\n")
        f.write(f"Haben→Sein Transformatie: {score.transformation_score:.2f}\n")
        f.write(f"Retoriek: {score.rhetorical_score:.2f}\n")
        f.write(f"Coherentie: {score.coherence_score:.2f}\n")
        f.write(f"Taal: {score.language_score:.2f}\n")
        f.write(f"Flow: {score.flow_score:.2f}\n")
        f.write(f"Humor: {score.humor_score:.2f}\n")
        f.write(f"Show Don't Tell multiplier: {score.sdt_score:.2f}\n")
        f.write(f"{'='*60}\n\n")
        f.write(sermon_text)

    # Prompt opslaan
    prompt_file = ITERATIONS_DIR / run_id / f"iter_{iteration:02d}_prompt.txt"
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    # Scores opslaan als JSON
    scores_file = ITERATIONS_DIR / run_id / f"iter_{iteration:02d}_scores.json"
    with open(scores_file, "w", encoding="utf-8") as f:
        json.dump({
            "iteration": iteration,
            "overall_score": score.overall_score,
            "stylometric_score": score.stylometric_score,
            "theological_score": score.theological_score,
            "metaphorical_score": score.metaphorical_score,
            "transformation_score": score.transformation_score,
            "rhetorical_score": score.rhetorical_score,
            "coherence_score": score.coherence_score,
            "language_score": score.language_score,
            "flow_score": score.flow_score,
            "humor_score": score.humor_score,
            "sdt_score": score.sdt_score,
            "is_best": is_best,
            "sermon_length": len(sermon_text),
        }, f, indent=2)

    # Als dit de beste is, maak ook een "best" symlink/copy
    if is_best:
        best_sermon = ITERATIONS_DIR / run_id / "best_sermon.txt"
        with open(best_sermon, "w", encoding="utf-8") as f:
            f.write(f"Beste iteratie: {iteration}\n")
            f.write(f"Score: {score.overall_score:.2f}\n")
            f.write(f"{'='*60}\n\n")
            f.write(sermon_text)

    return sermon_file


def create_feedback_block(solutions: list[Solution]) -> str:
    """Creëer een feedback block van eerdere oplossingen."""
    if not solutions:
        return ""

    # Sorteer op score (beste eerst)
    sorted_solutions = sorted(solutions, key=lambda x: x.score, reverse=True)
    selected = sorted_solutions[:MAX_SOLUTIONS_IN_FEEDBACK]

    blocks = []
    for i, sol in enumerate(selected, 1):
        blocks.append(f"""--- Poging {i} (score: {sol.score:.2f}) ---
Feedback: {sol.feedback}
""")

    return "\n".join(blocks)


async def generate_sermon(
    scripture_text: str,
    scripture_context: str,
    reference_sermons: list[str],
    system_prompt: str,
    previous_solutions: list[Solution] | None = None,
) -> tuple[str, str, int, int]:
    """
    Genereer een preek gegeven een Bijbeltekst.
    Returns: (sermon_text, used_prompt, input_tokens, output_tokens)
    """
    current_prompt = system_prompt

    # Voeg feedback toe als er eerdere pogingen zijn
    if previous_solutions:
        # Selecteer random subset
        selected = [
            s for s in previous_solutions
            if random.random() < SELECTION_PROBABILITY
        ]
        if selected:
            feedback_block = create_feedback_block(selected)
            current_prompt += FEEDBACK_ADDITION.format(feedback_block=feedback_block)

    # Voeg voorbeelden van echte preken toe
    examples = ""
    if reference_sermons:
        examples = "\n\nVOORBEELDEN VAN JÜNGEL-STIJL (ter inspiratie, niet om te kopiëren):\n"
        num_examples = min(NUM_REFERENCE_EXAMPLES, len(reference_sermons))
        selected_sermons = random.sample(reference_sermons, num_examples)
        for i, ref in enumerate(selected_sermons, 1):
            # Neem een groot fragment van de preek
            start = EXAMPLE_FRAGMENT_START
            end = start + EXAMPLE_FRAGMENT_LENGTH
            fragment = ref[start:end]
            # Voeg ellipsis toe als we niet de hele preek hebben
            suffix = "..." if end < len(ref) else ""
            examples += f"\n--- Voorbeeld {i} ---\n{fragment}{suffix}\n"

    user_message = f"""Schrijf een preek over de volgende Bijbeltekst:

BIJBELTEKST: {scripture_text}

CONTEXT: {scripture_context}
{examples}

Schrijf nu een volledige Jüngel-preek over deze tekst. Zorg dat de preek minimaal 10.000 karakters is."""

    response, input_tokens, output_tokens = await call_claude(
        model=GENERATOR_MODEL,
        system_prompt=current_prompt,
        user_message=user_message,
        temperature=GENERATOR_TEMPERATURE,
        max_tokens=GENERATOR_MAX_TOKENS,
    )

    return response, current_prompt, input_tokens, output_tokens


async def generate_with_iteration(
    scripture_text: str,
    scripture_context: str,
    reference_sermons: list[str],
    max_iterations: int = MAX_ITERATIONS,
    target_score: float = 0.8,
    verbose: bool = True,
    save_best_prompt: bool = True,
    save_iterations: bool = True,
) -> GeneratedSermon:
    """
    Genereer een preek met iteratieve verbetering.
    Stopt wanneer target_score bereikt is of max_iterations bereikt.

    Het systeem:
    1. Laadt het beste beschikbare prompt als startpunt
    2. Evolueert het prompt op basis van feedback
    3. Slaat elke iteratie op naar disk (indien save_iterations=True)
    4. Slaat het beste prompt op voor toekomstig gebruik
    """
    solutions: list[Solution] = []
    best_result: Optional[GeneratedSermon] = None
    best_score = -1.0
    best_prompt = ""
    all_learnings: list[str] = []

    total_input_tokens = 0
    total_output_tokens = 0

    # Unieke run ID voor deze sessie
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Laad het beste prompt als startpunt
    base_prompt, parent_version = get_best_prompt_for_evolution()

    if verbose:
        stats = get_prompt_stats()
        if stats["total_versions"] > 0:
            print(f"Geladen prompt v{parent_version} (beste score tot nu: {stats['best_score']:.2f})")
        else:
            print("Startend met basis prompt (geen eerdere versies)")
        if save_iterations:
            print(f"Iteraties worden opgeslagen in: output/iterations/{run_id}/")

    current_prompt = base_prompt

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n--- Iteratie {iteration + 1}/{max_iterations} ---")

        # Genereer preek
        sermon_text, used_prompt, in_tok, out_tok = await generate_sermon(
            scripture_text=scripture_text,
            scripture_context=scripture_context,
            reference_sermons=reference_sermons,
            system_prompt=current_prompt,
            previous_solutions=solutions if iteration > 0 else None,
        )
        total_input_tokens += in_tok
        total_output_tokens += out_tok

        # Score de preek
        score = await compute_full_score(
            generated_sermon=sermon_text,
            scripture_text=scripture_text,
            reference_sermons=reference_sermons,
        )

        if verbose:
            print(f"Lengte: {len(sermon_text)} karakters")
            print(f"Stilometrische score: {score.stylometric_score:.2f}")
            print(f"Theologie (Kreuzestheologie): {score.theological_score:.2f}")
            print(f"Metaforische Waarheid: {score.metaphorical_score:.2f}")
            print(f"Haben→Sein Transformatie: {score.transformation_score:.2f}")
            print(f"Retorische score: {score.rhetorical_score:.2f}")
            print(f"Coherentie score: {score.coherence_score:.2f}")
            print(f"Taal score: {score.language_score:.2f}")
            print(f"Flow score: {score.flow_score:.2f}")
            print(f"Humor score: {score.humor_score:.2f}")
            print(f"Show Don't Tell multiplier: {score.sdt_score:.2f}")
            print(f"Overall score: {score.overall_score:.2f}")

        result = GeneratedSermon(
            text=sermon_text,
            score=score,
            iteration=iteration + 1,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            final_prompt=used_prompt,
            prompt_version=parent_version,
        )

        # Update beste resultaat
        is_new_best = score.overall_score > best_score
        if is_new_best:
            best_score = score.overall_score
            best_result = result
            best_prompt = used_prompt
            if verbose:
                print(f"Nieuwe beste score: {best_score:.2f}")

        # Sla iteratie op naar disk
        if save_iterations:
            saved_path = save_iteration(
                run_id=run_id,
                iteration=iteration + 1,
                sermon_text=sermon_text,
                score=score,
                prompt=used_prompt,
                is_best=is_new_best,
            )
            if verbose:
                print(f"Opgeslagen: {saved_path.name}")

        # Check of target bereikt
        if score.overall_score >= target_score:
            if verbose:
                print(f"Target score {target_score} bereikt!")

            # Sla het succesvolle prompt op
            if save_best_prompt:
                stored = store_prompt(
                    system_prompt=used_prompt,
                    score=score.overall_score,
                    scripture_text=scripture_text,
                    iteration=iteration + 1,
                    tokens_used=total_input_tokens + total_output_tokens,
                    parent_version=parent_version if parent_version > 0 else None,
                    improvements=all_learnings if all_learnings else None,
                )
                result.prompt_version = stored.version

            return result

        # Voeg toe aan solutions voor feedback
        combined_feedback = (
            f"Stilometrie: {score.stylometric_feedback}\n"
            f"LLM feedback: {score.llm_feedback}"
        )
        solutions.append(Solution(
            sermon=sermon_text,
            feedback=combined_feedback,
            score=score.overall_score,
        ))

        # Extraheer learnings en evolueer het prompt
        new_learnings = extract_learnings_from_feedback(combined_feedback, score.overall_score)
        if new_learnings:
            all_learnings.extend(new_learnings)
            current_prompt = evolve_prompt(base_prompt, all_learnings)
            if verbose:
                print(f"Prompt geëvolueerd met {len(new_learnings)} nieuwe inzichten")

    if verbose:
        print(f"\nMax iteraties bereikt. Beste score: {best_score:.2f}")

    # Sla het beste prompt op
    if save_best_prompt and best_result:
        stored = store_prompt(
            system_prompt=best_prompt,
            score=best_score,
            scripture_text=scripture_text,
            iteration=best_result.iteration,
            tokens_used=total_input_tokens + total_output_tokens,
            parent_version=parent_version if parent_version > 0 else None,
            improvements=all_learnings if all_learnings else None,
        )
        best_result.prompt_version = stored.version

    return best_result or result
