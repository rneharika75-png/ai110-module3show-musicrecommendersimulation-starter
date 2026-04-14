# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify or YouTube learn your taste from millions of listening events — what you skipped, replayed, or added to a playlist — and use that signal to predict what people similar to you also enjoyed (collaborative filtering). This simulation takes a simpler, more transparent approach: content-based filtering. Instead of learning from behavior, it directly compares the attributes of each song to what the user says they want. There is no hidden learning, no user history, and no black-box model — every score can be read off a formula. The priority here is explainability: you can always see exactly why a song was recommended.

### `Song` features used

| Feature | Type | Role in scoring |
|---|---|---|
| `genre` | categorical | Categorical match — worth +2.00 pts (all-or-nothing) |
| `mood` | categorical | Categorical match — worth +1.00 pts (all-or-nothing) |
| `energy` | float (0–1) | Similarity score — up to +1.00 pts |
| `valence` | float (0–1) | Similarity score — up to +0.50 pts |
| `acousticness` | float (0–1) | Similarity score — up to +0.25 pts |
| `title`, `artist` | string | Display only, not used in scoring |
| `tempo_bpm`, `danceability` | float | Loaded but not weighted in this version |

### `UserProfile` / `user_prefs` fields

| Field | Type | Description |
|---|---|---|
| `genre` | str | Preferred genre (e.g. `"pop"`, `"lofi"`) |
| `mood` | str | Preferred mood (e.g. `"happy"`, `"chill"`) |
| `energy` | float (0–1) | Target energy level |
| `valence` | float (0–1) | Target emotional positivity (optional) |
| `acousticness` | float (0–1) | Texture preference (optional) |

### Scoring Rule (one song)

```
similarity(pref, value) = 1.0 - |pref - value|   ← rewards closeness, not just high/low

score = +2.00  if genre matches          (all-or-nothing)
      + +1.00  if mood matches           (all-or-nothing)
      + +1.00 × energy similarity        (0.00 – 1.00)
      + +0.50 × valence similarity       (0.00 – 0.50)
      + +0.25 × acousticness similarity  (0.00 – 0.25)
      ─────────────────────────────────
        max possible score: 4.75
```

Genre is worth double mood because it defines the entire sonic universe of a song — a mood match across genre boundaries rarely feels satisfying.

### Ranking Rule (list of songs)

Every song in the catalog is scored, then sorted descending. The top `k` results are returned, each with a breakdown showing exactly how many points each feature contributed.

---

### Algorithm Recipe

The complete decision rules the system uses, in priority order:

| Step | Rule | Max points |
|---|---|---|
| 1 | Award **+2.00** if `song.genre == user.genre` | 2.00 |
| 2 | Award **+1.00** if `song.mood == user.mood` | 1.00 |
| 3 | Award `1.00 × (1 − \|song.energy − user.energy\|)` | 1.00 |
| 4 | Award `0.50 × (1 − \|song.valence − user.valence\|)` | 0.50 |
| 5 | Award `0.25 × (1 − \|song.acousticness − user.acousticness\|)` | 0.25 |
| 6 | Sort all songs by total score descending, return top `k` | — |

**Total possible score: 4.75**

Steps 1 and 2 are binary — a song either earns the full points or zero. Steps 3–5 always contribute a partial score, rewarding songs that are *close* to the user's target even when they are not an exact match.

---

### Known Biases

- **Genre over-weighting.** At +2.00, a genre match is worth more than a perfect mood + energy combination (+1.00 + up to 1.00). A great song that matches the user's mood and energy exactly but belongs to a slightly different genre (e.g. `indie pop` vs `pop`) will always score lower than a mediocre song in the right genre. The system may bury good cross-genre discoveries.

- **Mood is all-or-nothing.** Moods exist on a spectrum — "relaxed" and "chill" are close, but the system treats them as completely different and awards zero points for a near-miss. A listener who wants "chill" gets no credit for a "relaxed" song, even though they are sonically similar.

- **Small catalog amplifies bias.** With only 20 songs, a genre with two entries (e.g. `lofi`) will always compete against genres with one entry. The ranking reflects catalog size as much as genuine fit.

- **No listening history.** The profile is static — it never updates based on what the user actually plays, skips, or replays. Real systems learn and adapt; this one does not.

---

### Sample Terminal Output

> **Screenshot:** *(replace this line by dragging your terminal screenshot here)*

```
Loaded songs: 20

============================================================
  MUSIC RECOMMENDER — Top 5 Results
  Profile: genre=pop  mood=happy  energy=0.85
============================================================

  #1  Sunrise City  (Neon Echo)
       [###################]  4.71 / 4.75
       Genre: pop   Mood: happy   Energy: 0.82
       Why:
         +2.00 genre matches 'pop'
         +1.00 mood matches 'happy'
         +0.97 energy (song=0.82, target=0.85)
         +0.49 valence (song=0.84, target=0.85)
         +0.24 acousticness (song=0.18, target=0.15)

  #2  Gym Hero  (Max Pulse)
       [##############-----]  3.60 / 4.75
       Genre: pop   Mood: intense   Energy: 0.93
       Why:
         +2.00 genre matches 'pop'
         +0.00 mood 'intense' != 'happy'
         +0.92 energy (song=0.93, target=0.85)
         +0.46 valence (song=0.77, target=0.85)
         +0.23 acousticness (song=0.05, target=0.15)

  #3  Rooftop Lights  (Indigo Parade)
       [##########---------]  2.59 / 4.75
       Genre: indie pop   Mood: happy   Energy: 0.76
       Why:
         +0.00 genre 'indie pop' != 'pop'
         +1.00 mood matches 'happy'
         +0.91 energy (song=0.76, target=0.85)
         +0.48 valence (song=0.81, target=0.85)
         +0.20 acousticness (song=0.35, target=0.15)

  #4  Overdrive Horizon  (Pulse Grid)
       [######-------------]  1.58 / 4.75
       Genre: edm   Mood: euphoric   Energy: 0.96
       Why:
         +0.00 genre 'edm' != 'pop'
         +0.00 mood 'euphoric' != 'happy'
         +0.89 energy (song=0.96, target=0.85)
         +0.47 valence (song=0.91, target=0.85)
         +0.22 acousticness (song=0.04, target=0.15)

  #5  Street Philosopher  (Kade Rivers)
       [######-------------]  1.57 / 4.75
       Genre: hip-hop   Mood: confident   Energy: 0.78
       Why:
         +0.00 genre 'hip-hop' != 'pop'
         +0.00 mood 'confident' != 'happy'
         +0.93 energy (song=0.78, target=0.85)
         +0.41 valence (song=0.67, target=0.85)
         +0.23 acousticness (song=0.08, target=0.15)

============================================================
```

---

### Data Flow

```mermaid
flowchart TD
    A["🎧 User Preferences\ngenre · mood · energy · valence · acousticness"]
    B["📄 data/songs.csv\n20 songs"]

    A --> REC
    B --> LOAD["load_songs()\nparse CSV → list of dicts"]
    LOAD --> REC["recommend_songs(user_prefs, songs, k)"]

    REC --> LOOP["for each song in catalog"]

    LOOP --> SCORE["score_song(user_prefs, song)"]

    SCORE --> G{genre\nmatch?}
    G -->|yes| G1["+2.00 pts"]
    G -->|no|  G0["+0.00 pts"]

    G1 --> M
    G0 --> M{mood\nmatch?}
    M -->|yes| M1["+1.00 pts"]
    M -->|no|  M0["+0.00 pts"]

    M1 --> EN["energy similarity\n× 1.00  →  0.00–1.00 pts"]
    M0 --> EN
    EN --> VA["valence similarity\n× 0.50  →  0.00–0.50 pts"]
    VA --> AC["acousticness similarity\n× 0.25  →  0.00–0.25 pts"]
    AC --> SUM["song score  (max 4.75)"]

    SUM --> LOOP
    LOOP -->|all songs scored| SORT["sort descending by score"]
    SORT --> TOPK["slice top-k"]
    TOPK --> OUT["✅ Top K Recommendations\ntitle · score / 4.75 · explanation"]
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

