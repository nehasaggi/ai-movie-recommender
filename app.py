import streamlit as st
import pandas as pd
from textblob import TextBlob

st.title("🎬 AI Movie Recommendation System")

# Load data
df = pd.read_csv("imdb_top_1000.csv")

# Extract genres
genres = sorted({g.strip() for xs in df["Genre"].dropna().str.split(", ") for g in xs})

# Sentiment label
def senti(p):
    return "😊 Positive" if p > 0 else "😞 Negative" if p < 0 else "😐 Neutral"

# Recommendation logic
def recommend(genre, mood_text, rating):
    d = df.copy()

    if genre:
        d = d[d["Genre"].str.contains(genre, case=False, na=False)]

    if rating:
        d = d[d["IMDB_Rating"] >= rating]

    results = []
    keywords = mood_text.lower().split()

    for _, row in d.iterrows():
        overview = row.get("Overview", "")
        if pd.isna(overview):
            continue

        pol = TextBlob(overview).sentiment.polarity
        keyword_score = sum(1 for word in keywords if word in overview.lower())

        score = (pol * 2) + (keyword_score * 1.5) + (row["IMDB_Rating"] / 10)

        results.append((row["Series_Title"], pol, score))

    results = sorted(results, key=lambda x: x[2], reverse=True)
    return results[:5]


# UI
name = st.text_input("Enter your name")
genre = st.selectbox("Select Genre", [""] + genres)
mood_text = st.text_input("How are you feeling today?")
rating = st.slider("Minimum Rating", 7.0, 9.5, 8.0)

if st.button("Recommend Movies"):
    if not name or not mood_text:
        st.warning("Please enter your name and mood!")
    else:
        recs = recommend(genre, mood_text, rating)

        st.success(f"🍿 Recommendations for {name}:")

        for i, (title, p, score) in enumerate(recs, 1):
            st.write(f"{i}. 🎥 {title} (⭐ {score:.2f}, {senti(p)})")

# Surprise
if st.button("🎲 Surprise Me"):
    row = df.sample(1).iloc[0]
    st.info(f"🎥 {row['Series_Title']} (⭐ {row['IMDB_Rating']})")
