"""
Stilometrische analyse en scoring voor Jüngel-preken.
Combineert stilometrische analyse met LLM-gebaseerde theologische beoordeling.
"""
import json
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import TypedDict

from config import (
    SCORER_MODEL,
    SCORER_TEMPERATURE,
    SCORER_MAX_TOKENS,
    STYLOMETRIC_TARGETS,
    THEOLOGICAL_WORD_TARGETS,
)
from llm import call_claude


class StylometricMetrics(TypedDict):
    char_count: int
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    sentence_length_std: float
    question_count: int
    question_ratio: float
    exclamation_count: int
    unique_words: int
    lexical_diversity: float
    comma_per_sentence: float
    colon_count: int


@dataclass
class SermonScore:
    """Score resultaat voor een gegenereerde preek."""
    overall_score: float
    stylometric_score: float
    stylometric_feedback: str
    llm_feedback: str
    theological_score: float
    metaphorical_score: float
    transformation_score: float
    rhetorical_score: float
    coherence_score: float
    language_score: float
    flow_score: float
    humor_score: float
    sdt_score: float  # Show Don't Tell discipline multiplier


# Scoring rubric voor LLM evaluatie
SCORING_SYSTEM_PROMPT = """Je bent een expert in de theologie en preekstijl van Eberhard Jüngel (1934-2021). Je taak is om een gegenereerde preek te beoordelen op hoe authentiek deze aanvoelt als een preek die Jüngel zelf zou kunnen houden.

JÜNGELS SYSTEMATISCH-THEOLOGISCHE KERN (Kreuzestheologie):

1. GOTTES SEIN IST IM WERDEN (Gods Zijn is in het Worden):
   - God is GEEN statisch, onveranderlijk wezen (de klassieke "actus purus")
   - Gods wezen is een DYNAMISCHE en RELATIONELE gebeurtenis van Liefde
   - Dit Worden is verankerd in de Geschichtlichkeit van Christus' leven, sterven en opstanding
   - De preek moet deze dynamiek weerspiegelen, niet een statisch Godsbeeld presenteren

2. GOTT ALS GEHEIMNIS DER WELT (God als Geheim van de Wereld):
   - God is een "geheim" niet omdat Hij ver is, maar omdat Hij niet in categorieën past
   - Zijn wezen wordt UITSLUITEND geopenbaard in het kruis - de Menschlichkeit Gottes
   - Radicaal christocentrisch: geen abstracte speculaties, alleen de concrete Christus
   - De preek moet dit geheim respecteren en niet proberen God te "vangen"

3. DE RECHTVAARDIGING VAN DE GODDELOZE:
   - Dit is de articulus stantis et cadentis ecclesiae
   - Rechtvaardiging is een performatief GEBEUREN van Gods spreken, geen status
   - Eenzijdig, van God uitgaand, de goddeloze betreffend
   - Solus Christus, sola gratia: het Woord des kruises is dwaasheid voor de rede maar Gods wijsheid

4. VAN HABEN NAAR SEIN (Van Bezitten naar Worden):
   - De hoorder moet transformeren van Habende (bezitter) naar Seiende (wordende)
   - Haben = existentie van bezit, prestatie, religieuze controle
   - Sein = existentie gevormd door genade, bevrijd van zelfrechtvaardiging
   - De preek moet deze existentiële transformatie bewerkstelligen

5. DIALOOG MET ATHEÏSME EN MODERNITEIT:
   - Wij leven in het "Zeitalter der sprachlichen Ortlosigkeit Gottes"
   - Het atheïsme is diagnostische kritiek op valse, onchristelijke Godsbeelden
   - De preek overstijgt theïsme EN atheïsme door de Gekruisigde

JÜNGELS HOMILETISCHE METHODE (Metaforische Waarheid):

1. DE METAFOOR ALS COMMUNICATIEMODUS:
   - De metafoor is SUPERIEUR voor theologisch taalgebruik, niet minderwaardig
   - De metafoor verbindt bekend en onbekend, onthult werkelijkheid
   - De waarheid zelf is metaforisch - een talig gebeuren waarin "zijn" wordt overgedragen
   - Gods Geheim moet metaforisch gecommuniceerd worden, niet rationalistisch gereduceerd

2. DE "TWEEDE NAÏVITEIT":
   - Vertel de "gevaarlijke geschiedenis van Jezus Christus" narratief
   - Creëer ruimte voor het eigen verhaal van de hoorder
   - Het kruis is de "spijker waar het Evangelie aan hangt" - historisch verankerd
   - Combineer post-metafysische taal met concrete Geschichtlichkeit

3. VERWONDERING (STAUNEN) ALS DOEL:
   - God dient zich "nooit vanzelfsprekend, altijd verrassend" aan
   - De metafoor onderbreekt de werkelijkheid, confronteert met Gods vreemde genade
   - Geen arrogante versimpeling - diepe inhoud in de taal van deze tijd

JÜNGELS RETORISCHE STIJL:
- Academisch maar WARM en pastoraal
- Lange, meanderende zinnen afgewisseld met korte klappers
- Paradoxen en contrasten ("Niet... maar...")
- Retorische vragen die DWINGEN mee te denken
- Verwijzingen naar filosofie (Heidegger) en literatuur (Schiller, Goethe, Hölderlin)
- Directe, hartelijke aanspraak; opbouw naar "doorbraak"-momenten
- Herhaling van kernzinnen; ironie en understatement

--- BEOORDELINGSCRITERIA ---

A. "SHOW, DON'T TELL" DISCIPLINE (EXTREEM BELANGRIJK):
Controleer of de volgende theologische concepten IMPLICIET worden getoond, en NIET EXPLICIET worden benoemd. Geef een zeer lage score (0-5) als een van de volgende letterlijke termen wordt gebruikt:
- "Gods zijn is in het worden" / "Gottes Sein ist im Werden"
- "Van hebben naar zijn" / "Haben naar Sein"
- "God als geheim van de wereld"
- "De rechtvaardiging van de goddeloze"
- "Kreuzestheologie" / "theologia crucis"
- Elke andere expliciete Jüngel-terminologie.
De preek moet de WAARHEID van deze concepten laten ZIEN door verhalen, beelden en de existentiële beweging, niet door ze te benoemen.

B. THEOLOGISCHE AUTHENTICITEIT (Gewogen op inhoud, niet op jargon):
1. DYNAMISCH GODSBEELD: Spreekt de preek over God in Zijn concrete handelen en toewending, of als een statische, verre grootheid? Is het kruis het venster op God?
2. GOD ALS GEHEIM: Respecteert de preek God als een geheim dat zich openbaart in Christus, of probeert het God in een systeem te vangen?
3. GENADE DIE VOORAFGAAT: Is de toon van de preek een geschenk, of legt het (subtiel) een prestatie-eis op de hoorder?
4. BEVRIJDING: Wordt het contrast tussen een leven van 'hebben' (prestatie, controle) en 'zijn' (genade) voelbaar gemaakt met concrete beelden?
5. EERLIJKHEID: Neemt de preek moderne twijfel serieus zonder de vreemdheid van het evangelie af te zwakken?

C. HOMILETISCHE EN RETORISCHE KWALITEIT:
1. METAFOREN: Zijn de metaforen rijk, ontsluitend en verrassend? Of zijn het platte illustraties?
2. STRUCTUUR EN FLOW: Volgt de preek de vloeiende structuur (opening, probleem, verdieping, spanning, doorbraak, toepassing)? Is er een duidelijke opbouw?
3. ZINSLENGTE VARIATIE: Worden lange, meanderende zinnen effectief afgewisseld met korte, krachtige 'klappers'?
4. PARADOXEN EN VRAGEN: Worden paradoxen en retorische vragen gebruikt om de hoorder aan het denken te zetten en vanzelfsprekendheden te doorbreken?
5. HUMOR EN LICHTHEID: Is er een vleugje ironie, understatement of warmte die de preek menselijk maakt en voorkomt dat deze zwaar op de hand wordt?
6. LENGTE: Voldoet de preek aan de vereiste lengte (10.000-15.000 karakters)?

--- BEOORDELINGSPROCES ---

Beoordeel de preek op de volgende aspecten (elk 0-10) en geef je beoordeling in een strikt JSON-formaat. Geef ALLEEN het JSON-object terug, zonder enige extra tekst of uitleg. Een perfecte Jüngel-preek scoort 9-10 op alle dimensies.

{
    "show_dont_tell_discipline": {
        "score": <0-10, waarbij 0-5 betekent dat expliciete termen zijn gebruikt>,
        "feedback": "<Specifieke feedback over het al dan niet benoemen van verboden termen. Citeer de fouten.>"
    },
    "theological_score": <0-10>,
    "metaphorical_score": <0-10>,
    "transformation_score": <0-10>,
    "rhetorical_score": <0-10>,
    "coherence_score": <0-10>,
    "language_score": <0-10>,
    "flow_score": <0-10>,
    "humor_score": <0-10>,
    "length_score": <0-10, waarbij 10 = perfecte lengte, 0 = veel te kort/lang>,
    "feedback_details": {
        "theological": "<feedback: Gottes Sein im Werden, Geheimnis, Rechtvaardiging>",
        "metaphorical": "<feedback: metaforische waarheid, tweede naïviteit, verwondering>",
        "transformation": "<feedback: Haben→Sein beweging, existentiële bevrijding>",
        "rhetorical": "<feedback over retoriek, paradoxen, vragen>",
        "coherence": "<feedback over samenhang en structuur>",
        "language_and_flow": "<feedback over taal, zinsbouw, ritme>",
        "humor": "<feedback over humor en lichtheid>"
    },
    "overall_assessment": "<Korte overall beoordeling met de belangrijkste verbeterpunten.>"
}"""


def analyze_sermon(text: str) -> tuple[StylometricMetrics, list[str]]:
    """Analyseer stilometrische kenmerken van een preek."""
    # Verwijder NBV21 header indien aanwezig
    text = re.sub(r'^NBV21\[.*?\]', '', text, flags=re.DOTALL).strip()

    # Zinnen splitsen
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

    # Woorden
    words = re.findall(r'\b\w+\b', text.lower())

    sentence_lengths = [len(s.split()) for s in sentences] if sentences else [0]

    metrics: StylometricMetrics = {
        'char_count': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'avg_sentence_length': statistics.mean(sentence_lengths) if sentences else 0,
        'sentence_length_std': statistics.stdev(sentence_lengths) if len(sentences) > 1 else 0,
        'question_count': text.count('?'),
        'question_ratio': text.count('?') / len(sentences) if sentences else 0,
        'exclamation_count': text.count('!'),
        'unique_words': len(set(words)),
        'lexical_diversity': len(set(words)) / len(words) if words else 0,
        'comma_per_sentence': text.count(',') / len(sentences) if sentences else 0,
        'colon_count': text.count(':'),
    }
    return metrics, words


def compute_theological_word_frequencies(words: list[str]) -> dict[str, float]:
    """Bereken frequenties van theologische kernwoorden per 1000 woorden."""
    word_freq = Counter(words)
    total = len(words)
    if total == 0:
        return {w: 0.0 for w in THEOLOGICAL_WORD_TARGETS}

    return {
        word: (word_freq.get(word, 0) / total) * 1000
        for word in THEOLOGICAL_WORD_TARGETS
    }


def score_metric_deviation(value: float, target: dict) -> float:
    """
    Score hoe dicht een metriek bij de target ligt.
    Returns een score tussen 0 en 1, waar 1 = perfect.
    """
    mean = target["mean"]
    std = target["std"]

    if std == 0:
        return 1.0 if value == mean else 0.0

    # Z-score berekenen
    z = abs(value - mean) / std

    # Score: 1.0 binnen 1 std, lineair aflopend tot 0 bij 3 std
    if z <= 1:
        return 1.0
    elif z >= 3:
        return 0.0
    else:
        return 1.0 - (z - 1) / 2


def compute_stylometric_score(metrics: StylometricMetrics, words: list[str]) -> tuple[float, dict]:
    """
    Bereken een overall stilometrische score.
    Returns (score, details) waar score tussen 0-1 ligt.
    """
    scores = {}

    # Score basismetrieken
    for metric_name, target in STYLOMETRIC_TARGETS.items():
        if metric_name in metrics:
            scores[metric_name] = score_metric_deviation(metrics[metric_name], target)

    # Score theologische woordfrequenties
    theo_freqs = compute_theological_word_frequencies(words)
    theo_scores = []
    for word, target_freq in THEOLOGICAL_WORD_TARGETS.items():
        actual_freq = theo_freqs.get(word, 0)
        # Tolerantie: binnen factor 2 van target
        if target_freq == 0:
            theo_scores.append(1.0 if actual_freq < 1 else 0.5)
        else:
            ratio = actual_freq / target_freq
            if 0.5 <= ratio <= 2.0:
                theo_scores.append(1.0)
            elif 0.25 <= ratio <= 4.0:
                theo_scores.append(0.5)
            else:
                theo_scores.append(0.0)

    scores["theological_vocabulary"] = statistics.mean(theo_scores) if theo_scores else 0.5

    # Gewogen gemiddelde
    weights = {
        "char_count": 2.0,           # Lengte is belangrijk
        "avg_sentence_length": 1.5,
        "sentence_length_std": 1.0,   # Variatie in zinslengtes
        "question_ratio": 1.0,
        "lexical_diversity": 1.5,
        "comma_per_sentence": 0.5,
        "theological_vocabulary": 2.0,  # Theologisch vocabulaire belangrijk
    }

    total_weight = sum(weights.get(k, 1.0) for k in scores)
    weighted_score = sum(scores[k] * weights.get(k, 1.0) for k in scores) / total_weight

    details = {
        "individual_scores": scores,
        "metrics": dict(metrics),
        "theological_frequencies": theo_freqs,
    }

    return weighted_score, details


def generate_stylometric_feedback(metrics: StylometricMetrics, words: list[str]) -> str:
    """Genereer tekstuele feedback over stilometrische afwijkingen."""
    _, details = compute_stylometric_score(metrics, words)
    scores = details["individual_scores"]

    feedback_parts = []

    # Lengte feedback
    char_count = metrics["char_count"]
    target = STYLOMETRIC_TARGETS["char_count"]
    if char_count < target["min"]:
        feedback_parts.append(f"De preek is te kort ({char_count} karakters). "
                            f"Jüngel-preken zijn typisch {target['min']}-{target['max']} karakters.")
    elif char_count > target["max"]:
        feedback_parts.append(f"De preek is te lang ({char_count} karakters). "
                            f"Jüngel-preken zijn typisch {target['min']}-{target['max']} karakters.")

    # Zinslengte feedback
    avg_len = metrics["avg_sentence_length"]
    target = STYLOMETRIC_TARGETS["avg_sentence_length"]
    if avg_len < target["min"]:
        feedback_parts.append(f"Zinnen zijn gemiddeld te kort ({avg_len:.1f} woorden). "
                            f"Streef naar ~{target['mean']:.0f} woorden per zin.")
    elif avg_len > target["max"]:
        feedback_parts.append(f"Zinnen zijn gemiddeld te lang ({avg_len:.1f} woorden). "
                            f"Streef naar ~{target['mean']:.0f} woorden per zin.")

    # Variatie feedback
    if scores.get("sentence_length_std", 1) < 0.5:
        feedback_parts.append("Er is te weinig variatie in zinslengte. "
                            "Jüngel wisselt korte en lange zinnen af voor retorisch effect.")

    # Vragen feedback
    if scores.get("question_ratio", 1) < 0.5:
        q_count = metrics["question_count"]
        if q_count == 0:
            feedback_parts.append("De preek bevat geen retorische vragen. "
                                "Jüngel gebruikt regelmatig vragen om de hoorder te betrekken.")
        elif q_count > 20:
            feedback_parts.append("Te veel vragen. Jüngel gebruikt vragen spaarzaam maar effectief.")

    # Theologisch vocabulaire feedback
    theo_freqs = details["theological_frequencies"]
    if theo_freqs.get("god", 0) < 5:
        feedback_parts.append("Het woord 'God' komt weinig voor. "
                            "In Jüngel-preken is God het centrale onderwerp.")
    if theo_freqs.get("jezus", 0) + theo_freqs.get("christus", 0) < 3:
        feedback_parts.append("Jezus/Christus wordt weinig genoemd. "
                            "Jüngel preekt christocentrisch.")

    if not feedback_parts:
        return "Stilometrisch gezien ligt de preek dicht bij Jüngels stijl."

    return "\n".join(feedback_parts)


def parse_llm_score(response: str) -> dict:
    """Parse de JSON response van de LLM scorer."""
    # Probeer JSON te extraheren
    try:
        # Soms zit er tekst omheen
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    # Fallback: lege scores
    return {
        "show_dont_tell_discipline": {"score": 5, "feedback": "Kon response niet parsen"},
        "theological_score": 5,
        "metaphorical_score": 5,
        "transformation_score": 5,
        "rhetorical_score": 5,
        "coherence_score": 5,
        "language_score": 5,
        "flow_score": 5,
        "humor_score": 5,
        "length_score": 5,
        "feedback_details": {
            "theological": "Parsing error",
            "metaphorical": "Parsing error",
            "transformation": "Parsing error",
            "rhetorical": "Parsing error",
            "coherence": "Parsing error",
            "language_and_flow": "Parsing error",
            "humor": "Parsing error",
        },
        "overall_assessment": "Kon LLM response niet parsen.",
    }


async def compute_full_score(
    generated_sermon: str,
    scripture_text: str,
    reference_sermons: list[str],
) -> SermonScore:
    """
    Bereken de volledige score voor een gegenereerde preek.
    Combineert stilometrische analyse met LLM-gebaseerde theologische beoordeling.
    """
    # Stilometrische analyse
    metrics, words = analyze_sermon(generated_sermon)
    stylometric_score, _ = compute_stylometric_score(metrics, words)
    stylometric_feedback = generate_stylometric_feedback(metrics, words)

    # LLM-gebaseerde score
    user_message = f"""Beoordeel de volgende preek:

BIJBELTEKST: {scripture_text}

PREEK:
{generated_sermon}

Geef je beoordeling in het gevraagde JSON-formaat."""

    response, _, _ = await call_claude(
        model=SCORER_MODEL,
        system_prompt=SCORING_SYSTEM_PROMPT,
        user_message=user_message,
        temperature=SCORER_TEMPERATURE,
        max_tokens=SCORER_MAX_TOKENS,
    )

    llm_scores = parse_llm_score(response)

    # Extraheer individuele scores (normaliseer naar 0-1)
    theological = llm_scores.get("theological_score", 5) / 10
    metaphorical = llm_scores.get("metaphorical_score", 5) / 10
    transformation = llm_scores.get("transformation_score", 5) / 10
    rhetorical = llm_scores.get("rhetorical_score", 5) / 10
    coherence = llm_scores.get("coherence_score", 5) / 10
    language = llm_scores.get("language_score", 5) / 10
    flow = llm_scores.get("flow_score", 5) / 10
    humor = llm_scores.get("humor_score", 5) / 10

    # Show don't tell penalty
    show_dont_tell = llm_scores.get("show_dont_tell_discipline", {})
    if isinstance(show_dont_tell, dict):
        sdt_score = show_dont_tell.get("score", 10) / 10
    else:
        sdt_score = 1.0

    # Gewogen overall score
    # Weights gebaseerd op het belang voor Jüngel-authenticiteit
    weights = {
        "theological": 0.20,
        "metaphorical": 0.15,
        "transformation": 0.15,
        "rhetorical": 0.15,
        "coherence": 0.10,
        "language": 0.10,
        "flow": 0.10,
        "humor": 0.05,
    }

    llm_overall = (
        theological * weights["theological"] +
        metaphorical * weights["metaphorical"] +
        transformation * weights["transformation"] +
        rhetorical * weights["rhetorical"] +
        coherence * weights["coherence"] +
        language * weights["language"] +
        flow * weights["flow"] +
        humor * weights["humor"]
    )

    # Combineer stilometrie en LLM, met SDT penalty
    # 30% stilometrie, 70% LLM, vermenigvuldigd met SDT factor
    combined_score = (0.3 * stylometric_score + 0.7 * llm_overall) * sdt_score

    # Maak feedback string
    feedback_details = llm_scores.get("feedback_details", {})
    overall_assessment = llm_scores.get("overall_assessment", "")

    llm_feedback = f"""Overall: {overall_assessment}
Theologisch: {feedback_details.get('theological', 'N/A')}
Metaforisch: {feedback_details.get('metaphorical', 'N/A')}
Transformatie: {feedback_details.get('transformation', 'N/A')}
Retoriek: {feedback_details.get('rhetorical', 'N/A')}
Coherentie: {feedback_details.get('coherence', 'N/A')}
Taal/Flow: {feedback_details.get('language_and_flow', 'N/A')}
Humor: {feedback_details.get('humor', 'N/A')}"""

    if isinstance(show_dont_tell, dict) and show_dont_tell.get("feedback"):
        llm_feedback += f"\nShow don't tell: {show_dont_tell['feedback']}"

    return SermonScore(
        overall_score=combined_score,
        stylometric_score=stylometric_score,
        stylometric_feedback=stylometric_feedback,
        llm_feedback=llm_feedback,
        theological_score=theological,
        metaphorical_score=metaphorical,
        transformation_score=transformation,
        rhetorical_score=rhetorical,
        coherence_score=coherence,
        language_score=language,
        flow_score=flow,
        humor_score=humor,
        sdt_score=sdt_score,
    )
