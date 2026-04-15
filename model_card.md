# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests songs from a small catalog based on a user's stated preferences for genre, mood, energy level, emotional brightness, and acoustic texture. It is designed for classroom exploration of how content-based recommender systems work — not for real music products. The system assumes the user knows exactly what they want and can express it as a dictionary of features. It makes no attempt to learn from listening history or infer preferences from behavior.

---

## 3. How the Model Works

Each song in the catalog is compared to the user's preferences feature by feature. Genre and mood are checked for an exact match — either you get full points or none. Energy, valence, and acousticness use a closeness formula: the nearer the song's value is to what you asked for, the more points it earns. Genre is worth the most (up to 2 points), because getting the sonic universe wrong feels jarring regardless of anything else. Mood is worth 1 point, and the three numerical features share the remaining 1.75 points. Every song is scored out of a maximum of 4.75, then sorted highest to lowest. The top 5 are returned with a breakdown showing exactly where each song's points came from.

---

## 4. Data

The catalog contains 20 songs across 17 genres and 16 moods, expanded manually from a 10-song starter set. Genres represented include pop, lofi, rock, jazz, classical, hip-hop, r&b, country, edm, metal, folk, reggae, blues, soul, ambient, synthwave, and indie pop. Most genres have exactly one song; only lofi (3 songs) and pop (2 songs) have more than one entry. The data was generated for simulation purposes and reflects a Western, English-language, contemporary music bias. Genres common outside that context — Afrobeats, K-pop, Latin, classical Indian, flamenco — are entirely absent.

---

## 5. Strengths

- **Explainable by design.** Every score includes a printed breakdown — the user always knows exactly which features contributed and by how much. There is no black box.
- **Well-calibrated for lofi and pop.** These are the two genres with multiple catalog entries, so the top results genuinely compete for the best match rather than filling slots arbitrarily.
- **Adversarial profiles behave predictably.** Conflicting preferences produce low scores (max 1.91/4.75 for "sad but energetic"), and the system correctly signals uncertainty rather than confidently returning wrong results.
- **Profile diversity.** The system handles genre-fluid listeners (null preference profile) without crashing — it defaults to recommending the most statistically average songs, which is a reasonable fallback.

---

## 6. Limitations and Bias

**Primary finding — the mood-driven cross-genre promotion bias:**
For the "Deep Intense Rock" profile (genre=rock, mood=intense), the system ranked Gym Hero — a pop song — at #2 with a score of 2.56, above Iron Cathedral (metal) at 1.62. This happened because Gym Hero shares the mood label "intense" with the user's preference, earning a full +1.00 mood bonus, while Iron Cathedral's mood is labeled "aggressive" and earns nothing. The system has no concept that metal is sonically adjacent to rock: every non-rock genre is treated as equally distant, so a pop song with a matching mood label beats a metal song with a more appropriate sonic profile. A weight experiment confirmed that doubling the energy weight did not fix this — Gym Hero's high energy (0.93) meant it benefited equally from the boost. The real fix requires partial genre credit (e.g. rock ≈ metal = 0.5 pts), which would need a genre-similarity lookup table beyond the current design.

**Additional biases identified:**

- **Catalog sparsity creates false confidence.** 15 of 17 genres have exactly one song. When a user requests classical music, slot #1 scores a perfect 4.75 and slots #2–5 are filled by acoustically similar but genre-unrelated songs. The system fills every slot without signaling that it ran out of relevant matches.

- **Mood is binary on a spectrum.** "Relaxed" and "chill" are emotionally close but score identically as mismatches. A user who wants "chill" gets no partial credit for a "relaxed" song, even though those labels describe overlapping listening states.

- **Genre filter bubble.** Genre is worth 42% of the maximum score (2.00/4.75). A mediocre song in the correct genre will always outscore a near-perfect song in a related genre. This suppresses cross-genre discovery even when the user might enjoy it.

- **Static profile, no learning.** The profile never updates from actual listening behavior. A user who skips every recommendation still gets the same results on the next run.

---

## 7. Evaluation

Six user profiles were tested: three designed to match well-represented catalog entries (High-Energy Pop, Chill Lofi Study, Deep Intense Rock), and three adversarial cases designed to stress-test edge behaviors. The High-Energy Pop and Chill Lofi profiles produced results that matched musical intuition — the correct songs ranked first with high scores and a meaningful gap below them. The Deep Intense Rock profile revealed the mood-driven cross-genre bias described above. The "Ghost Genre" (classical) profile exposed the catalog-sparsity problem: a perfect 4.75 at #1 followed by a cliff to 1.52 at #2. The "Null Preference" profile showed that removing categorical preferences collapses the score range to 1.49–1.59/4.75 — essentially a tie — confirming that the system relies heavily on genre and mood to differentiate results. A weight-shift experiment (genre 2.00→1.00, energy 1.00→2.00) was run; it made results more spread but did not fix the Gym Hero ranking problem.

---

## 8. Future Work

- **Partial genre credit.** Build a genre-similarity map so that rock≈metal≈punk earn 0.5 pts instead of 0. This is the single highest-impact fix identified during testing.
- **Mood grouping.** Cluster moods into families (e.g. "chill/relaxed/peaceful", "intense/aggressive/energetic") so near-miss moods earn partial points.
- **Diversity injection.** After scoring, apply a penalty for consecutive results from the same genre or artist so the top-5 list is more varied.
- **Implicit feedback loop.** Track which songs the user skips or replays and adjust weights over time — moving from content-based filtering toward a hybrid system.
- **Larger, balanced catalog.** Expand to at least 5 songs per genre so every genre has meaningful within-genre competition.

---

## 9. Personal Reflection

Building this recommender showed that even a simple formula with five features and clear math can produce surprising and occasionally unfair results. The most unexpected discovery was that the "mood" weight — which seemed reasonable — ended up promoting pop songs for a rock listener simply because both shared the word "intense." This mirrors a real problem in production systems: labels and categories that seem precise can smuggle in assumptions that only become visible when you stress-test with adversarial inputs. It also reinforced that explainability is not just a nice-to-have: being able to print exactly where every point came from made it possible to diagnose the Gym Hero bug in seconds. A black-box model would have returned the same wrong answer with no trace of why.
