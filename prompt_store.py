"""
Dynamisch prompt management systeem.
Slaat prompts op, laadt de beste, en evolueert ze over tijd.
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


PROMPTS_DIR = Path(__file__).parent / "prompts"
PROMPT_HISTORY_FILE = PROMPTS_DIR / "prompt_history.json"
CURRENT_BEST_FILE = PROMPTS_DIR / "current_best.json"


@dataclass
class StoredPrompt:
    """Een opgeslagen prompt met metadata."""
    system_prompt: str
    score: float
    timestamp: str
    scripture_text: str
    iteration: int
    tokens_used: int
    version: int
    parent_version: Optional[int] = None
    improvements: Optional[list[str]] = None


def ensure_prompts_dir():
    """Zorg dat de prompts directory bestaat."""
    os.makedirs(PROMPTS_DIR, exist_ok=True)


def load_prompt_history() -> list[dict]:
    """Laad de volledige prompt geschiedenis."""
    ensure_prompts_dir()
    if not PROMPT_HISTORY_FILE.exists():
        return []
    with open(PROMPT_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_prompt_history(history: list[dict]):
    """Sla de prompt geschiedenis op."""
    ensure_prompts_dir()
    with open(PROMPT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def get_current_best() -> Optional[StoredPrompt]:
    """Haal het huidige beste prompt op."""
    ensure_prompts_dir()
    if not CURRENT_BEST_FILE.exists():
        return None
    with open(CURRENT_BEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return StoredPrompt(**data)


def save_current_best(prompt: StoredPrompt):
    """Sla het nieuwe beste prompt op."""
    ensure_prompts_dir()
    with open(CURRENT_BEST_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(prompt), f, indent=2, ensure_ascii=False)


def get_next_version() -> int:
    """Bepaal het volgende versienummer."""
    history = load_prompt_history()
    if not history:
        return 1
    return max(p.get("version", 0) for p in history) + 1


def store_prompt(
    system_prompt: str,
    score: float,
    scripture_text: str,
    iteration: int,
    tokens_used: int,
    parent_version: Optional[int] = None,
    improvements: Optional[list[str]] = None,
) -> StoredPrompt:
    """
    Sla een nieuw prompt op en update current_best indien nodig.
    Returns: het opgeslagen StoredPrompt object.
    """
    version = get_next_version()

    stored = StoredPrompt(
        system_prompt=system_prompt,
        score=score,
        timestamp=datetime.now().isoformat(),
        scripture_text=scripture_text,
        iteration=iteration,
        tokens_used=tokens_used,
        version=version,
        parent_version=parent_version,
        improvements=improvements,
    )

    # Voeg toe aan geschiedenis
    history = load_prompt_history()
    history.append(asdict(stored))
    save_prompt_history(history)

    # Update current_best als dit beter is
    current_best = get_current_best()
    if current_best is None or score > current_best.score:
        save_current_best(stored)
        print(f"Nieuw beste prompt opgeslagen (v{version}, score: {score:.2f})")

    return stored


def get_best_prompt_for_evolution() -> tuple[str, int]:
    """
    Haal het beste prompt op om verder te evolueren.
    Returns: (system_prompt, version)
    """
    best = get_current_best()
    if best:
        return best.system_prompt, best.version

    # Fallback naar basis prompt
    from generator import BASE_SYSTEM_PROMPT
    return BASE_SYSTEM_PROMPT, 0


def evolve_prompt(
    base_prompt: str,
    feedback_learnings: list[str],
) -> str:
    """
    Evolueer een prompt door geleerde lessen toe te voegen.

    Args:
        base_prompt: Het huidige prompt
        feedback_learnings: Lijst van geleerde verbeterpunten

    Returns:
        Geëvolueerd prompt met nieuwe inzichten
    """
    if not feedback_learnings:
        return base_prompt

    # Zoek de plek om learnings toe te voegen (voor de STRUCTUUR sectie)
    learnings_section = "\n\nGELEERDE VERBETERINGEN (uit eerdere iteraties):\n"
    for i, learning in enumerate(feedback_learnings[-10:], 1):  # Max 10 learnings
        learnings_section += f"- {learning}\n"

    # Voeg toe na de RETORISCHE STIJL sectie
    if "STRUCTUUR:" in base_prompt:
        parts = base_prompt.split("STRUCTUUR:")
        evolved = parts[0] + learnings_section + "\nSTRUCTUUR:" + parts[1]
    else:
        evolved = base_prompt + learnings_section

    return evolved


def extract_learnings_from_feedback(feedback: str, score: float) -> list[str]:
    """
    Extraheer concrete verbeterpunten uit feedback.
    Alleen nuttig als de score laag was (we leren van fouten).
    """
    if score > 0.8:
        # Bij hoge scores, leer wat goed ging
        return []

    learnings = []

    # Parse feedback voor concrete punten
    lines = feedback.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Filter op actionable feedback
        if any(keyword in line.lower() for keyword in [
            'te kort', 'te lang', 'te weinig', 'te veel',
            'ontbreekt', 'mist', 'zou moeten', 'probeer',
            'voeg toe', 'vermijd', 'gebruik meer', 'gebruik minder'
        ]):
            # Maak er een instructie van
            if not line.startswith('-'):
                line = line.replace('De preek is', 'Vermijd dat de preek')
                line = line.replace('Er is', 'Zorg voor')
            learnings.append(line)

    return learnings[:5]  # Max 5 learnings per iteratie


def get_prompt_stats() -> dict:
    """Haal statistieken op over prompt-evolutie."""
    history = load_prompt_history()
    if not history:
        return {"total_versions": 0, "best_score": 0, "avg_score": 0}

    scores = [p["score"] for p in history]
    return {
        "total_versions": len(history),
        "best_score": max(scores),
        "avg_score": sum(scores) / len(scores),
        "latest_version": history[-1]["version"],
        "score_improvement": scores[-1] - scores[0] if len(scores) > 1 else 0,
    }
