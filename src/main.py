"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # -----------------------------------------------------------------------
    # TASTE PROFILE
    # -----------------------------------------------------------------------
    # This profile represents a user who wants high-energy, upbeat music with
    # a bright emotional tone and a mostly electronic/produced texture.
    #
    # CRITIQUE — can this profile tell "intense rock" from "chill lofi"?
    #
    #   With only genre + mood + energy (the old 3-field version):
    #     Storm Runner  (rock/intense, energy=0.91): energy proximity = 0.89
    #     Library Rain  (lofi/chill,   energy=0.35): energy proximity = 0.55
    #     The gap exists but is narrow (~0.08 total score difference).
    #     A "moody synthwave" at energy=0.75 would score almost the same
    #     as intense rock — the profile can't separate them.
    #
    #   Adding valence + acousticness closes that gap:
    #     Storm Runner  (valence=0.48, acousticness=0.10):
    #       valence proximity   = 1 - |0.85 - 0.48| = 0.63
    #       acousticness proxy  = 1 - |0.15 - 0.10| = 0.95  ← strong match
    #     Library Rain  (valence=0.60, acousticness=0.86):
    #       valence proximity   = 1 - |0.85 - 0.60| = 0.75
    #       acousticness proxy  = 1 - |0.15 - 0.86| = 0.29  ← penalised
    #     Now chill lofi is clearly down-ranked on acousticness even when
    #     its valence is closer. The two vibes separate cleanly.
    #
    #   Remaining narrowness risk: genre="pop" locks out rock/lofi matches
    #   at the genre layer (0.30 weight), so this profile is intentionally
    #   pop-centric. To test genre-agnostic energy matching, remove "genre".
    # -----------------------------------------------------------------------
    user_prefs = {
        "genre":        "pop",    # strong filter — pop-centric taste
        "mood":         "happy",  # upbeat, positive emotional state
        "energy":       0.85,     # high energy — driving, not background
        "valence":      0.85,     # bright / optimistic tone
        "acousticness": 0.15,     # mostly produced/electronic texture
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # -----------------------------------------------------------------------
    # OUTPUT — clean terminal layout
    # -----------------------------------------------------------------------
    width = 60
    print("\n" + "=" * width)
    print("  MUSIC RECOMMENDER — Top 5 Results")
    print(f"  Profile: genre={user_prefs['genre']}  mood={user_prefs['mood']}"
          f"  energy={user_prefs['energy']}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Score bar: each full block = 0.25 pts, max 19 blocks (4.75 / 0.25)
        filled = round(score / 4.75 * 19)
        bar = "[" + "#" * filled + "-" * (19 - filled) + "]"

        print(f"\n  #{rank}  {song['title']}  ({song['artist']})")
        print(f"       {bar}  {score:.2f} / 4.75")
        print(f"       Genre: {song['genre']}   Mood: {song['mood']}"
              f"   Energy: {song['energy']}")
        print("       Why:")
        for reason in explanation.split("; "):
            print(f"         {reason}")

    print("\n" + "=" * width + "\n")


if __name__ == "__main__":
    main()
