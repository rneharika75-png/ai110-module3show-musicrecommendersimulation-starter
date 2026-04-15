# 🎧 Model Card — Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder takes a user's music preferences and finds the best matching songs from a catalog. It looks at what genre, mood, and energy level you want, then gives you the top 5 songs that match closest. It does not learn from you over time — it just scores and ranks based on what you tell it right now.

---

## 3. Data Used

The catalog has 20 songs. Each song has 9 features: id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. 17 different genres are covered (pop, lofi, rock, jazz, metal, classical, and more) and 16 different moods. Most genres only have 1 song, which is a real limitation. The data was created for this simulation — it does not represent real streaming data and does not include non-Western genres like Afrobeats, K-pop, or Latin music.

---

## 4. Algorithm Summary

The recommender works like a point system. For each song it asks:

- Does the genre match? If yes, +2 points.
- Does the mood match? If yes, +1 point.
- How close is the energy to what the user wants? Up to +1 point.
- How close is the valence (brightness)? Up to +0.5 points.
- How close is the acousticness? Up to +0.25 points.

The max score a song can get is 4.75. Once every song is scored, the list is sorted from highest to lowest and the top 5 are shown with a reason breakdown.

---

## 5. Observed Behavior / Biases

The biggest bias found was with the "Deep Intense Rock" profile. The system ranked Gym Hero — a pop song — as #2, above Iron Cathedral which is a metal song. This happened because Gym Hero had the same mood label ("intense") as the user wanted, so it earned a full +1 mood point. Iron Cathedral's mood is "aggressive" which is different in the system even though metal is way more similar to rock than pop is. The system treats all genres as equally different from each other, so it has no way to know that metal is closer to rock than pop is. Genre and mood matching is all-or-nothing — there is no partial credit for being close. This also means moods like "relaxed" and "chill" are treated as completely different even though they feel similar. Another issue is that 15 out of 17 genres only have 1 song, so if your genre matches, slot #1 is great but slots #2-5 are filled by whatever is numerically closest — not actually relevant.

---

## 6. Evaluation Process

Six different user profiles were tested. Three were normal: High-Energy Pop, Chill Lofi Study, and Deep Intense Rock. Three were adversarial (edge cases designed to find problems): a "Sad but Energetic" profile with conflicting preferences, a "Ghost Genre" classical profile where only one song matched, and a "Null Preference" profile with no genre or mood set. The High-Energy Pop and Chill Lofi profiles felt right — the top results matched what you would expect. The rock profile revealed the Gym Hero bias. The null profile showed that without genre or mood, all scores clustered between 1.49 and 1.59 out of 4.75, which is basically a tie. A weight experiment was also run where the genre weight was cut in half and the energy weight was doubled — it made scores more spread out but did not fix the Gym Hero problem.

---

## 7. Intended Use and Non-Intended Use

**Intended use:** This is a classroom simulation. It is meant to show how a simple content-based recommender works, how weights affect results, and where biases show up. It is a learning tool.

**Not intended for:** Real music recommendations to real users. The catalog is too small, the profile is static, and the system has no way to learn your actual taste. It should not be used to decide what music to surface on a real platform.

---

## 8. Ideas for Improvement

1. **Partial genre credit.** Right now rock and metal both score 0 for a rock user. A genre-similarity map where rock ≈ metal = 0.5 pts would fix the Gym Hero problem.
2. **Mood grouping.** Group similar moods together (chill, relaxed, peaceful) so near-miss moods earn partial points instead of zero.
3. **More songs per genre.** With only 1 song per genre for most genres, there is no real competition within a genre after the first match. At least 5 songs per genre would make the ranking meaningful.

---

## 9. Personal Reflection

The biggest learning moment was seeing how a math formula that looks totally reasonable on paper can still produce a result that feels obviously wrong. The Gym Hero situation was a good example — the weights made sense individually but combining them caused a pop song to outrank a metal song for a rock listener. That was not something I expected before running the tests.

Using AI tools helped a lot with writing the scoring logic and the algorithm recipe quickly. But I had to double-check the results by actually running the profiles and comparing them to what felt right musically. The AI wrote code that worked — but whether it was recommending the right things required human judgment.

What surprised me most was how much a simple 5-feature formula could feel like a real recommendation. When Sunrise City scored 4.65 out of 4.75 for the High-Energy Pop profile with a full breakdown showing exactly why, it felt convincing even though the math underneath is just addition. Real systems like Spotify use millions of data points and still make strange recommendations sometimes — so the gap between "simple simulation" and "real product" is smaller than I thought.

If I kept working on this, I would add the genre-similarity map first, then try connecting it to a real API to pull actual song data instead of a hand-built CSV.
