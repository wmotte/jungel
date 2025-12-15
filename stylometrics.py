"""
Stilometrische analyse en scoring voor Jüngel-preken.
"""
import re
import statistics
from collections import Counter
from typing import TypedDict

from config import STYLOMETRIC_TARGETS, THEOLOGICAL_WORD_TARGETS


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
