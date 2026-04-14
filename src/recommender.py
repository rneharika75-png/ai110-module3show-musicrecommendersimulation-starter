from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs for the given user profile."""
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-English explanation of why a song was recommended."""
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with all numeric fields cast to float/int."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


# ---------------------------------------------------------------------------
# ALGORITHM RECIPE  (point-based scoring)
# ---------------------------------------------------------------------------
#
# POINT VALUES — what each feature is worth at a perfect match:
#
#   +2.00  genre match       (categorical, all-or-nothing)
#   +1.00  mood match        (categorical, all-or-nothing)
#   up to +1.00  energy      (similarity: 1.0 - |pref - value|)
#   up to +0.50  valence     (similarity: 1.0 - |pref - value|)
#   up to +0.25  acousticness(similarity: 1.0 - |pref - value|)
#   ─────────────────────────────────────────────────────────
#   Max possible score: 4.75
#
# RATIONALE — why genre outweighs mood (2.0 vs 1.0):
#   Genre defines the entire sonic universe of a song: its instruments,
#   production style, and rhythmic feel. A metal fan hearing classical
#   will be jarred even if the mood label matches. Mood is a filter
#   *within* a genre, not a substitute for it.
#   → Genre mismatch is a bigger problem than mood mismatch.
#
# RATIONALE — why mood outweighs energy (1.0 vs up to 1.0):
#   Mood is a named human-readable label; a perfect mood match is a
#   clear signal. Energy is continuous and always contributes a partial
#   score, so even a mismatch still adds points. In practice mood gets
#   full 1.0 or 0.0, while energy averages ~0.7 across the catalog.
#
# RATIONALE — similarity formula for numerical features:
#   points = max_points × (1.0 - |user_pref - song_value|)
#   This rewards *closeness*, not just high or low raw values.
#   Example: user wants energy 0.85, song has 0.91:
#     points = 1.0 × (1 - |0.85 - 0.91|) = 1.0 × 0.94 = 0.94
#   A song at 0.40 would only earn 1.0 × 0.55 = 0.55 — clearly lower.
#
# RANKING RULE:
#   Score every song → sort descending → return top-k.
#   Scoring Rule answers "how good is THIS song?"
#   Ranking Rule answers "which k songs are BEST overall?"
# ---------------------------------------------------------------------------

POINTS = {
    "genre":        2.00,   # categorical — genre defines the sonic universe
    "mood":         1.00,   # categorical — primary vibe label
    "energy":       1.00,   # numerical  — intensity/drive
    "valence":      0.50,   # numerical  — emotional brightness
    "acousticness": 0.25,   # numerical  — texture (electronic vs organic)
}


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences (max 4.75) and return (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    # --- Categorical: genre (+2.0 if match, +0 otherwise) ---
    if "genre" in user_prefs:
        if song["genre"] == user_prefs["genre"]:
            score += POINTS["genre"]
            reasons.append(f"+{POINTS['genre']:.2f} genre matches '{song['genre']}'")
        else:
            reasons.append(f"+0.00 genre '{song['genre']}' != '{user_prefs['genre']}'")

    # --- Categorical: mood (+1.0 if match, +0 otherwise) ---
    if "mood" in user_prefs:
        if song["mood"] == user_prefs["mood"]:
            score += POINTS["mood"]
            reasons.append(f"+{POINTS['mood']:.2f} mood matches '{song['mood']}'")
        else:
            reasons.append(f"+0.00 mood '{song['mood']}' != '{user_prefs['mood']}'")

    # --- Numerical: energy  (up to +1.0) ---
    if "energy" in user_prefs:
        similarity = 1.0 - abs(user_prefs["energy"] - song["energy"])
        pts = POINTS["energy"] * similarity
        score += pts
        reasons.append(f"+{pts:.2f} energy (song={song['energy']}, target={user_prefs['energy']})")

    # --- Numerical: valence  (up to +0.5) ---
    if "valence" in user_prefs:
        similarity = 1.0 - abs(user_prefs["valence"] - song["valence"])
        pts = POINTS["valence"] * similarity
        score += pts
        reasons.append(f"+{pts:.2f} valence (song={song['valence']}, target={user_prefs['valence']})")

    # --- Numerical: acousticness  (up to +0.25) ---
    if "acousticness" in user_prefs:
        similarity = 1.0 - abs(user_prefs["acousticness"] - song["acousticness"])
        pts = POINTS["acousticness"] * similarity
        score += pts
        reasons.append(f"+{pts:.2f} acousticness (song={song['acousticness']}, target={user_prefs['acousticness']})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort by score descending, and return the top-k as (song, score, explanation) tuples."""
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        total_score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no matching preferences"
        scored.append((song, total_score, explanation))

    # Sort by score descending — this is the Ranking Rule
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
