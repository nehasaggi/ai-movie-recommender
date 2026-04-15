import time, pandas as pd
from textblob import TextBlob
from colorama import init, Fore

# Init colors
init(autoreset=True)

# Load CSV
try:
    df = pd.read_csv("imdb_top_1000.csv")
except FileNotFoundError:
    print(Fore.RED + "Error: The file 'imdb_top_1000.csv' was not found.")
    raise SystemExit

# Unique genres
genres = sorted({g.strip() for xs in df["Genre"].dropna().str.split(", ") for g in xs})


def dots():
    """Prints ... with delay (AI thinking effect)."""
    for _ in range(3):
        print(Fore.YELLOW + ".", end="", flush=True)
        time.sleep(0.5)


def senti(p):
    """Polarity -> label."""
    return "Positive 😊" if p > 0 else "Negative 😞" if p < 0 else "Neutral 😐"


# 🔥 ADVANCED RECOMMEND FUNCTION
def recommend(genre=None, mood=None, rating=None, mood_text="", n=5):
    d = df.copy()

    # Genre filter
    if genre:
        d = d[d["Genre"].str.contains(genre, case=False, na=False)]

    # Rating filter
    if rating is not None:
        d = d[d["IMDB_Rating"] >= rating]

    if d.empty:
        return "No suitable movie recommendations found."

    results = []
    keywords = mood_text.lower().split()

    for _, row in d.iterrows():
        overview = row.get("Overview", "")
        if pd.isna(overview):
            continue

        overview_lower = overview.lower()

        # Sentiment
        pol = TextBlob(overview).sentiment.polarity

        # Keyword match score
        keyword_score = sum(1 for word in keywords if word in overview_lower)

        # Final AI score
        score = (pol * 2) + (keyword_score * 1.5) + (row["IMDB_Rating"] / 10)

        if mood is None or pol >= 0:
            results.append((row["Series_Title"], pol, score))

    if not results:
        return "No suitable movie recommendations found."

    # Sort by best score
    results = sorted(results, key=lambda x: x[2], reverse=True)

    return results[:n]


def show(recs, name):
    """Display recommendations nicely."""
    print(f"\n🍿 AI-Analyzed Movie Recommendations for {name}:")

    for i, (title, p, score) in enumerate(recs, 1):
        print(f"{i}. 🎥 {title} (Score: {score:.2f}, {senti(p)})")


def get_genre():
    """Get valid genre input."""
    print("\nAvailable Genres:")
    for i, g in enumerate(genres, 1):
        print(f"{i}. {g}")

    while True:
        choice = input("Enter genre number or name: ")

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(genres):
                return genres[idx - 1]

        if choice in genres:
            return choice

        print("Invalid input. Try again.\n")


def get_rating():
    """Get rating filter."""
    while True:
        r = input("Enter minimum rating (7.6 to 9.3) or 'skip': ").strip().lower()

        if r == "skip":
            return None

        try:
            val = float(r)
            if 7.6 <= val <= 9.3:
                return val
            else:
                print("Rating out of range. Try again.\n")
        except:
            print("Invalid input. Try again.\n")


# 🎲 SURPRISE FEATURE
def surprise():
    row = df.sample(1).iloc[0]
    print("\n🎲 Surprise Movie Pick!")
    print(f"🎥 {row['Series_Title']} (⭐ {row['IMDB_Rating']})")


# ================= MAIN =================

print(Fore.CYAN + "🎬 Welcome to AI Movie Recommender!")
name = input("Enter your name: ")
print(Fore.GREEN + f"Hello {name}! Let's find a movie for you.")

print("\n🔍 Let's get started...")

genre = get_genre()
mood_text = input("Describe your mood in one line: ")

print("Analyzing mood", end="")
dots()

mood_pol = TextBlob(mood_text).sentiment.polarity
print(f"\nYour mood seems {senti(mood_pol)}")

rating = get_rating()

print(f"Finding movies for {name}", end="")
dots()

recs = recommend(genre, mood_pol, rating, mood_text)

if isinstance(recs, str):
    print(Fore.RED + recs)
else:
    show(recs, name)


# 🔁 LOOP
while True:
    again = input("\nWould you like more recommendations? (yes/no/surprise): ").strip().lower()

    if again == "no":
        print("🎉 Enjoy your movie time!")
        break

    elif again == "yes":
        recs = recommend(genre, mood_pol, rating, mood_text)
        if isinstance(recs, str):
            print(Fore.RED + recs)
        else:
            show(recs, name)

    elif again == "surprise":
        surprise()

    else:
        print("Invalid choice. Please type yes, no, or surprise.")
