"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles — three normal and three adversarial/edge-case —
to stress-test the scoring logic and reveal biases.
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# OUTPUT HELPER
# ---------------------------------------------------------------------------

def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted top-k results block for one user profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)
    width = 62

    prefs_summary = "  ".join(
        f"{k}={v}" for k, v in user_prefs.items()
    )

    print("\n" + "=" * width)
    print(f"  PROFILE: {label}")
    print(f"  {prefs_summary}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        filled = round(score / 4.75 * 19)
        bar = "[" + "#" * filled + "-" * (19 - filled) + "]"

        print(f"\n  #{rank}  {song['title']}  ({song['artist']})")
        print(f"       {bar}  {score:.2f} / 4.75")
        print(f"       Genre: {song['genre']:<12} Mood: {song['mood']:<12} Energy: {song['energy']}")
        print("       Why:")
        for reason in explanation.split("; "):
            print(f"         {reason}")

    print("\n" + "=" * width)


# ---------------------------------------------------------------------------
# USER PROFILES
# ---------------------------------------------------------------------------

# --- Normal profiles ---

HIGH_ENERGY_POP = {
    "genre":        "pop",
    "mood":         "happy",
    "energy":       0.90,
    "valence":      0.85,
    "acousticness": 0.10,
}

CHILL_LOFI = {
    "genre":        "lofi",
    "mood":         "chill",
    "energy":       0.38,
    "valence":      0.58,
    "acousticness": 0.80,
}

DEEP_INTENSE_ROCK = {
    "genre":        "rock",
    "mood":         "intense",
    "energy":       0.95,
    "valence":      0.45,
    "acousticness": 0.10,
}

# --- Adversarial / edge-case profiles ---

# Conflicting preferences: high energy (0.92) but sad mood.
# Energy pulls toward metal/edm/rock; mood=sad only matches "3am Confession"
# (blues, energy=0.29). These preferences fight each other — expect confused ranking.
SAD_BUT_ENERGETIC = {
    "mood":         "sad",
    "energy":       0.92,
    "valence":      0.25,
    "acousticness": 0.10,
}

# Ghost genre: only one classical song exists (Moonlit Sonata).
# After that single genre match, the system has nothing left to filter on —
# the remaining 4 slots are filled by numerical similarity alone.
# Reveals catalog-sparsity bias.
CLASSICAL_PEACEFUL = {
    "genre":        "classical",
    "mood":         "peaceful",
    "energy":       0.18,
    "valence":      0.88,
    "acousticness": 0.97,
}

# Null categorical preferences: no genre or mood specified.
# Every song earns 0 pts on the categorical features, so the entire
# ranking is driven by numerical proximity to mid-range values.
# Reveals what the system recommends when it knows nothing about your taste.
NULL_PREFERENCE = {
    "energy":       0.50,
    "valence":      0.50,
    "acousticness": 0.50,
}


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    print_recommendations("High-Energy Pop",    HIGH_ENERGY_POP,    songs)
    print_recommendations("Chill Lofi Study",   CHILL_LOFI,         songs)
    print_recommendations("Deep Intense Rock",  DEEP_INTENSE_ROCK,  songs)
    print_recommendations("Sad but Energetic (adversarial)",  SAD_BUT_ENERGETIC,  songs)
    print_recommendations("Ghost Genre — Classical (adversarial)", CLASSICAL_PEACEFUL, songs)
    print_recommendations("Null Preference (adversarial)",    NULL_PREFERENCE,    songs)

    print()


if __name__ == "__main__":
    main()
