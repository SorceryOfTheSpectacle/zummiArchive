#!/usr/bin/env python3
"""
Zummi Archive Analysis Tool

Read-only analysis of archived posts. Never modifies source files.
Run from the repo root: python3 analysis/analyse.py
"""

import re
import sys
from collections import Counter
from pathlib import Path

ARCHIVE_PATH = Path(__file__).parent.parent / "archived" / "2014-04-23_EverySingleOneOfZummiPosts_from_pastebin"

# Thinkers/authors Zummi references
THINKERS = [
    ("Plato", ["plato", "platonic", "platonist"]),
    ("Marx", ["marx", "marxist", "marxism"]),
    ("Jung", ["jung", "jungian"]),
    ("Derrida", ["derrida"]),
    ("Zizek", ["zizek"]),
    ("McLuhan", ["mcluhan"]),
    ("Debord", ["debord", "debords"]),
    ("Girard", ["girard"]),
    ("Crowley", ["crowley"]),
    ("Heidegger", ["heidegger"]),
    ("Nietzsche", ["nietzsche", "nietzschean"]),
    ("Wittgenstein", ["wittgenstein"]),
    ("Lacan", ["lacan", "lacanian"]),
    ("Foucault", ["foucault"]),
    ("Bateson", ["bateson"]),
    ("Agamben", ["agamben"]),
    ("Vico", ["vico"]),
    ("Deleuze", ["deleuze"]),
    ("Husserl", ["husserl"]),
    ("Hayles", ["hayles"]),
    ("Dekerckhove", ["dekerckhove", "dekerckhoves"]),
    ("Weber", ["weber"]),
    ("Augustine", ["augustine"]),
    ("Eliade", ["eliade"]),
    ("Schmitt", ["schmitt"]),
    ("Strauss", ["straussian", "strauss"]),
    ("Joyce", ["joyce"]),
    ("Baudrillard", ["baudrillard"]),
    ("Benjamin", ["benjamin"]),
    ("Adorno", ["adorno"]),
    ("Graeber", ["graeber"]),
    ("Guattari", ["guattari"]),
    ("Badiou", ["badiou"]),
    ("Schlain", ["schlain"]),
    ("Ramey", ["ramey"]),
    ("Quine", ["quine"]),
    ("Searle", ["searle"]),
    ("Nicoll", ["nicoll"]),
    ("Pickstock", ["pickstock"]),
    ("Aristotle", ["aristotle"]),
    ("Ebert", ["ebert"]),
]

# Key recurring concepts to count
CONCEPTS = [
    "spectacle",
    "gnostic",
    "cybernetics",
    "enantiodromia",
    "consciousness",
    "language",
    "myth",
    "alchemy",
    "occult",
    "magic",
    "logos",
    "alphabet",
    "christian",
    "memory",
    "ideology",
    "capitalism",
    "recursion",
    "dissociation",
    "philosophy",
    "wisdom",
    "soul",
    "archetype",
    "semiotic",
    "signifier",
    "cathexis",
    "libidinal",
    "tao",
    "neoplatonism",
    "hermetic",
    "spectrology",
    "hyperstition",
    "telegram",
    "reddit",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "not",
    "it", "its", "that", "this", "these", "those", "i", "you", "he",
    "she", "we", "they", "me", "him", "her", "us", "them", "my", "your",
    "his", "our", "their", "what", "which", "who", "when", "where", "why",
    "how", "all", "any", "both", "each", "more", "most", "other", "some",
    "such", "no", "nor", "only", "own", "same", "so", "than", "too",
    "very", "just", "about", "up", "out", "if", "then", "into", "through",
    "there", "here", "much", "also", "because", "think", "know", "like",
    "get", "one", "thing", "things", "really", "even", "i'm", "don't",
    "it's", "that's", "i've", "they're", "what's", "becuase", "bc",
    "im", "ive", "dont", "thats", "its", "youre", "theyre", "hes",
    "shes", "weve", "theyve", "wont", "cant", "isnt", "arent", "wasnt",
    "werent", "hasnt", "havent", "hadnt", "doesnt", "didnt", "wouldnt",
    "couldnt", "shouldnt",
}


def load_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    # Strip markdown link syntax but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Strip HTML entities
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    return text


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [w.strip("'") for w in words if w.strip("'")]


def count_thinkers(text_lower: str) -> list[tuple[str, int]]:
    results = []
    for name, variants in THINKERS:
        count = sum(
            len(re.findall(r'\b' + re.escape(v) + r'\b', text_lower))
            for v in variants
        )
        if count > 0:
            results.append((name, count))
    return sorted(results, key=lambda x: -x[1])


def count_concepts(text_lower: str) -> list[tuple[str, int]]:
    results = []
    for concept in CONCEPTS:
        count = len(re.findall(r'\b' + re.escape(concept), text_lower))
        if count > 0:
            results.append((concept, count))
    return sorted(results, key=lambda x: -x[1])


def top_words(tokens: list[str], n: int = 40) -> list[tuple[str, int]]:
    filtered = [t for t in tokens if t not in STOPWORDS and len(t) > 3]
    return Counter(filtered).most_common(n)


def sentence_count(text: str) -> int:
    return len(re.findall(r'[.!?]+', text))


def unique_words(tokens: list[str]) -> int:
    return len(set(tokens))


def avg_word_len(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return sum(len(t) for t in tokens) / len(tokens)


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_table(rows: list[tuple], col1: str = "Item", col2: str = "Count", width: int = 30) -> None:
    print(f"  {col1:<{width}} {col2}")
    print(f"  {'-' * width} ------")
    for name, count in rows:
        print(f"  {name:<{width}} {count}")


def main() -> None:
    if not ARCHIVE_PATH.exists():
        print(f"Archive not found: {ARCHIVE_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading: {ARCHIVE_PATH.name}")
    text = load_text(ARCHIVE_PATH)
    text_lower = text.lower()
    tokens = tokenize(text)

    total_words = len(tokens)
    unique = unique_words(tokens)
    sentences = sentence_count(text)
    chars = len(text)
    avg_len = avg_word_len(tokens)
    lexical_density = unique / total_words if total_words else 0

    print_section("TEXT STATISTICS")
    stats = [
        ("Total characters", f"{chars:,}"),
        ("Total words", f"{total_words:,}"),
        ("Unique words", f"{unique:,}"),
        ("Lexical density", f"{lexical_density:.3f}"),
        ("Sentences (approx)", f"{sentences:,}"),
        ("Avg word length", f"{avg_len:.2f} chars"),
    ]
    for label, val in stats:
        print(f"  {label:<25} {val}")

    print_section("THINKERS & AUTHORS REFERENCED")
    thinker_counts = count_thinkers(text_lower)
    if thinker_counts:
        print_table(thinker_counts, col1="Name")
    else:
        print("  (none found)")

    print_section("KEY CONCEPTS (occurrences)")
    concept_counts = count_concepts(text_lower)
    if concept_counts:
        print_table(concept_counts, col1="Concept")
    else:
        print("  (none found)")

    print_section("TOP 40 CONTENT WORDS (excl. stopwords)")
    top = top_words(tokens, n=40)
    print_table(top, col1="Word")

    print(f"\n{'=' * 60}")
    print("  Done. Source files were not modified.")
    print('=' * 60)


if __name__ == "__main__":
    main()
