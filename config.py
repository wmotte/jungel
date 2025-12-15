"""
Configuratie voor de Jüngel preek-generator.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API configuratie
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model configuratie
GENERATOR_MODEL = "claude-opus-4-5"  # Voor preek-generatie
SCORER_MODEL = "claude-sonnet-4-5"      # Voor scoring (goedkoper dan Opus voor iteraties)
FINAL_EVAL_MODEL = "claude-opus-4-5"   # Voor finale evaluatie

# Generator parameters
GENERATOR_TEMPERATURE = 0.8
GENERATOR_MAX_TOKENS = 8000

# Scorer parameters
SCORER_TEMPERATURE = 0.3
SCORER_MAX_TOKENS = 2000

# Iteratie parameters
MAX_ITERATIONS = 5
MAX_SOLUTIONS_IN_FEEDBACK = 3
SELECTION_PROBABILITY = 0.8

# Few-shot example parameters
NUM_REFERENCE_EXAMPLES = 5      # Aantal voorbeeldpreken per generatie
EXAMPLE_FRAGMENT_START = 100    # Start positie in de preek (skip header)
EXAMPLE_FRAGMENT_LENGTH = 12000 # Lengte van het fragment (~85% van gemiddelde preek)


# Stilometrische targets (gebaseerd op Jüngel-corpus analyse)
STYLOMETRIC_TARGETS = {
    "char_count": {"mean": 14278, "std": 3145, "min": 9600, "max": 21500},
    "avg_sentence_length": {"mean": 15.88, "std": 1.83, "min": 13, "max": 21},
    "sentence_length_std": {"mean": 10.27, "std": 1.72, "min": 7, "max": 15},
    "question_ratio": {"mean": 0.05, "std": 0.04, "min": 0, "max": 0.14},
    "lexical_diversity": {"mean": 0.29, "std": 0.03, "min": 0.22, "max": 0.36},
    "comma_per_sentence": {"mean": 0.78, "std": 0.20, "min": 0.37, "max": 1.31},
}

# Theologische kernwoorden frequenties (per 1000 woorden)
THEOLOGICAL_WORD_TARGETS = {
    "god": 9.7,      # 736 / 76000 woorden * 1000
    "jezus": 5.3,
    "christus": 3.7,
    "liefde": 2.7,
    "leven": 4.8,
    "dood": 2.5,
    "wereld": 5.5,
    "woord": 1.5,
}
