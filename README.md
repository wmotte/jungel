# Jüngel Sermon Generator

Een experimenteel project dat verkent of generatieve taalmodellen de homiletische stijl van een specifieke predikant kunnen leren en toepassen op nieuwe Bijbelteksten.

**Website:** https://wmotte.github.io/jungel/

---

## Inleiding

### Het probleem

Voorgangers lezen preken van vakgenoten ter lering en vermaak. Ondanks verschillen in context, theologie en homiletische benadering valt er veel op te steken van de verbeeldingskracht die het schrijven van een preek vereist. Een beperking daarbij is dat van de meeste predikanten slechts preken over een beperkt deel van de Schrift beschikbaar zijn.

Toch rijst soms de vraag: *"Hoe zou deze predikant over een andere tekst hebben gepreekt?"*

### De experimentele aanpak

Dit project onderzoekt of generatieve taalmodellen homiletische patronen kunnen herkennen en toepassen. De basis wordt gevormd door 32 preken van de Duitse theoloog Eberhard Jüngel (1934-2021), handmatig en vrij letterlijk vertaald naar het Nederlands. Deze preken, oorspronkelijk verschenen in de zevendelige reeks [*Predigten*](https://www.radius-verlag.de/buecher/theologisches/152/predigten-1-7) (Stuttgart: Radius-Verlag GmbH, 2013), behandelen nieuwtestamentische teksten.

Fragmenten uit deze vertaalde preken, gecombineerd met een zorgvuldig samengesteld set aan homiletische instructies, maken het mogelijk om deze predikant andere teksten te laten "bepreken" waarbij (hopelijk) iets van de oorspronkelijke verbeeldingskracht postuum "geactiveerd" wordt.

### Verantwoording

De gegenereerde teksten dienen als **uitgangspunt voor eigen reflectie**, niet als kant-en-klare preken. Het systeem streeft naar inspiratiemateriaal dat de karakteristieke denkbewegingen en retorische patronen van Jüngel weerspiegelt, zonder te pretenderen dat dit authentieke Jüngel-preken zijn.

---

## Over Eberhard Jüngel

Eberhard Jüngel (1934-2021) was een invloedrijke Duitse protestantse theoloog, verbonden aan de Universiteit van Tübingen. Zijn denken kenmerkt zich door:

### Theologische kernthema's

| Concept | Betekenis |
|---------|-----------|
| **Gottes Sein ist im Werden** | God is geen statisch wezen, maar openbaart zich dynamisch in de geschiedenis, vooral in Christus |
| **Gott als Geheimnis der Welt** | God laat zich niet vangen in menselijke categorieën, maar openbaart zich in het kruis |
| **Rechtvaardiging van de goddeloze** | Gods genade gaat vooraf aan menselijke prestatie - de kern van het lutherse evangelie |
| **Van Haben naar Sein** | De transformatie van een "hebbend" bestaan (prestatie, controle) naar een "wordend" bestaan (genade) |

### Homiletische stijl

Jüngel's preken zijn herkenbaar aan:

- **Paradoxale formuleringen**: "God wordt mens", "in de dood is het leven"
- **Retorische vragen**: die de hoorder dwingen mee te denken
- **Lange, meanderende zinnen** afgewisseld met korte, krachtige "klappers"
- **Literaire en filosofische citaten**: Hölderlin, Goethe, Schiller, Heidegger
- **Academisch maar warm**: intellectueel diepgaand, toch pastoraal toegankelijk
- **Ironie en understatement**: lichtheid te midden van ernst

---

## Hoe het werkt

### Iteratieve optimalisatie

Het systeem genereert niet één keer een preek, maar doorloopt een iteratieve feedback-loop. Dit is geïnspireerd door de [Poetiq ARC-AGI solver](https://poetiq.ai/posts/arcagi_announcement/), die via iteratieve verbetering state-of-the-art resultaten behaalde.

```
┌─────────────────────────────────────────────────────────────┐
│                   ITERATIEVE LOOP                           │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Generator   │───▶│    Scorer    │───▶│   Feedback   │   │
│  │  (Claude)    │    │ (Stilo+LLM)  │    │   Aggregator │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         ▲                                        │          │
│         └────────────────────────────────────────┘          │
│                    (max 5 iteraties)                        │
└─────────────────────────────────────────────────────────────┘
```

**Per iteratie:**
1. **Generator** produceert een preek op basis van de Bijbeltekst en het huidige prompt
2. **Scorer** beoordeelt de preek op meerdere dimensies (zie hieronder)
3. **Feedback** wordt geaggregeerd en teruggevoerd naar de generator
4. Het **prompt evolueert** op basis van geleerde verbeterpunten

### Prompt evolutie

Het systeem "leert" over tijd door succesvolle prompts op te slaan en te hergebruiken:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   v1 (base)     │────▶│   v2 (+3 tips)  │────▶│   v3 (+5 tips)  │
│   score: 0.65   │     │   score: 0.72   │     │   score: 0.81   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

Bij elke run wordt het beste beschikbare prompt geladen. Feedback uit eerdere iteraties wordt omgezet in concrete verbeterpunten die in het prompt worden geïntegreerd.

---

## Scoring Systeem

De scoring combineert **deterministische stilometrie** (objectief meetbaar) met **LLM-beoordeling** (kwalitatief):

### Score-componenten

| Component | Gewicht | Methode |
|-----------|---------|---------|
| Stilometrie | 30% | Deterministisch: lengte, zinslengte, variatie, theologisch vocabulaire |
| Theologie | 20% | LLM: Herkenbaar Jüngeliaans? Gods "ja", genade, kruis/opstanding |
| Metaforisch | 15% | LLM: Rijke, ontsluitende metaforen; verwondering |
| Transformatie | 15% | LLM: Hebben→Zijn beweging, existentiële bevrijding |
| Retoriek | 15% | LLM: Paradoxen, contrasten, retorische vragen |
| Coherentie | 10% | LLM: Rode draad, opbouw naar climax |
| Taal | 10% | LLM: Academisch maar pastoraal, zinslengte-variatie |
| Flow | 10% | LLM: Ritme, tempo, korte "klappers" |
| Humor | 5% | LLM: Ironie, understatement, lichtheid |

### Show Don't Tell Multiplier (SDT)

Een cruciaal aspect van authentieke Jüngel-preken is dat theologische concepten **getoond** worden, niet expliciet **benoemd**. Het systeem straft preken af die vakjargon gebruiken:

```
overall_score = (0.3 * stilometrie + 0.7 * llm_score) * sdt_multiplier
```

**Verboden expliciete termen** (resulteren in lage SDT score):
- "Gods zijn is in het worden" / "Gottes Sein ist im Werden"
- "Van hebben naar zijn" / "Haben naar Sein"
- "God als geheim van de wereld"
- "De rechtvaardiging van de goddeloze"
- "Kreuzestheologie" / "theologia crucis"

Een preek moet de *waarheid* van deze concepten laten zien door verhalen, beelden en existentiële beweging - niet door ze te benoemen.

### Stilometrische Targets

Gebaseerd op corpus-analyse van 32 echte Jüngel-preken:

| Metriek | Gemiddelde | Std | Range |
|---------|------------|-----|-------|
| Lengte | 14.278 chars | 3.145 | 9.600 - 21.500 |
| Zinslengte | 15.9 woorden | 1.8 | 13 - 21 |
| Zinslengte variatie | 10.3 | 1.7 | 7 - 15 |
| Vraag-ratio | 5% | 4% | 0 - 14% |
| Lexicale diversiteit | 0.29 | 0.03 | 0.22 - 0.36 |

---

## Installatie

### Vereisten
- Python 3.10+
- Anthropic API key

### Stappen

```bash
# Clone repository
git clone https://github.com/wmotte/jungel.git
cd jungel

# Maak virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# of: .venv\Scripts\activate  # Windows

# Installeer dependencies
pip install -r requirements.txt

# Configureer API key
cp .env.example .env
# Edit .env en voeg je ANTHROPIC_API_KEY toe
```

---

## Gebruik

### CLI Interface

```bash
python main.py
```

Dit toont een menu met opties:

1. **Demo**: Genereer een preek voor een standaard Bijbeltekst (Jakobus 5:13-18)
2. **Custom**: Genereer een preek voor een eigen Bijbeltekst
3. **Bekijk prompt**: Toon het huidige beste prompt met metadata
4. **Geschiedenis**: Toon alle prompt-versies met scores

### Programmatisch gebruik

```python
import asyncio
from generator import generate_with_iteration

async def main():
    result = await generate_with_iteration(
        scripture_text="Matteüs 5:9",
        scripture_context="Gelukkig de vredestichters, want zij zullen kinderen van God genoemd worden.",
        reference_sermons=alle_preken_als_referentie,  # List[str]
        max_iterations=5
    )
    print(result.text)
    print(f"Score: {result.score.overall_score:.2f}")
    print(f"SDT multiplier: {result.score.sdt_score:.2f}")

asyncio.run(main())
```

---

## Project Structuur

```
jungel/
├── config.py          # API keys, model settings, stilometrische targets
├── llm.py             # Claude API wrapper
├── scorer.py          # Gecombineerde scoring (stilometrie + LLM)
├── prompt_store.py    # Dynamisch prompt management en evolutie
├── generator.py       # Iteratieve preek-generator met feedback loop
├── main.py            # CLI interface
├── stylometrics.py    # Stilometrische analyse utilities
│
├── docs/              # Website bestanden (GitHub Pages)
│   ├── index.html     # Preek-lezer interface
│   ├── prompt.md      # Homiletische instructies (publiek)
│   ├── preek_*.json   # Vertaalde originele preken
│   ├── paulus_*.json  # Vertaalde originele preken (Paulus-corpus)
│   └── mogelijk_*.json # Gegenereerde preken
│
├── prompts/           # Opgeslagen prompts (automatisch aangemaakt)
│   ├── current_best.json
│   └── prompt_history.json
│
├── output/            # Gegenereerde preken en iteratie-logs
│   └── iterations/    # Per-run iteratie bestanden
│
├── vertaling_Wim/     # Bronbestanden vertalingen
│   └── export/        # Geëxporteerde JSON preken
│
└── requirements.txt   # Python dependencies
```

---

## Configuratie

In `config.py` kun je aanpassen:

```python
# Modellen
GENERATOR_MODEL = "claude-opus-4-5"    # Voor preek-generatie
SCORER_MODEL = "claude-sonnet-4-5"     # Voor scoring (goedkoper)

# Iteratie parameters
MAX_ITERATIONS = 5              # Max pogingen per preek
MAX_SOLUTIONS_IN_FEEDBACK = 3   # Aantal eerdere pogingen in feedback
SELECTION_PROBABILITY = 0.8     # Kans dat een oplossing in feedback komt

# Few-shot examples
NUM_REFERENCE_EXAMPLES = 5      # Aantal voorbeeldpreken per generatie
EXAMPLE_FRAGMENT_LENGTH = 12000 # Lengte van voorbeeldfragmenten
```

---

## Beperkingen en overwegingen

### Methodologische beperkingen

1. **Geen objectieve ground truth**: Anders dan bij puzzels (ARC-AGI) is er geen "correcte" preek. De scoring blijft een benadering van menselijk oordeel.

2. **LLM-als-scorer**: Een LLM die een andere LLM scoort kan leiden tot patronen die de scorer hoog waardeert maar niet authentiek Jüngeliaans zijn. Dit is een bekend probleem bij evaluatie door taalmodellen.

3. **Beperkt corpus**: 32 preken is relatief weinig data. Stilistische patronen kunnen overfitted zijn op specifieke teksten.

### Theologische overwegingen

4. **Stijl ≠ inhoud**: Het systeem kan retorische patronen reproduceren, maar de diepe theologische intuïties die Jüngels denken voeden zijn niet direct overdraagbaar.

5. **Inspiratie, geen vervanging**: Gegenereerde preken zijn bedoeld als startpunt voor reflectie, niet als kant-en-klare preekvoorstellen.

---

## Toekomstige mogelijkheden

- [ ] **Blind-test**: Mix gegenereerde en echte preken voor menselijke beoordeling
- [ ] **A/B testing interface**: Voor theologen om preken te vergelijken
- [ ] **Fine-tuning**: Op Jüngel-corpus indien voldoende data beschikbaar
- [ ] **Uitbreiding**: Naar andere theologen (Barth, Moltmann, Noordmans, Sölle)
- [ ] **Interactieve feedback**: Menselijke input (o.a. exegese) en correcties terug in de loop

---

## Referenties

### Technisch
- Poetiq ARC-AGI solver: [Traversing the Frontier of Superintelligence](https://poetiq.ai/posts/arcagi_announcement/)

### Theologisch
- Eberhard Jüngel: *Gott als Geheimnis der Welt* (1977)
- Eberhard Jüngel: [*Predigten*](https://www.radius-verlag.de/buecher/theologisches/152/predigten-1-7), 7 delen (Radius-Verlag, 2013)
- Rudolf Otto: *Das Heilige* (1917) - mysterium tremendum et fascinans

### Corpus
- 32 Nederlandse vertalingen van Jüngel-preken (vert. Wim Otte)

---

## Licentie

Dit project is bedoeld voor educatief en experimenteel gebruik.
