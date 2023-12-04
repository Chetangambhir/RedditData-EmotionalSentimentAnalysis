import sqlite3
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # For emotion analysis using VADER

# Connect to your SQLite database
conn = sqlite3.connect('reddit_data.db')  # Replace 'your_database.db' with your database file path
cursor = conn.cursor()

# Select the title and full story content from your database
cursor.execute("SELECT title, full_story FROM reddit_posts")
data = cursor.fetchall()

# Create a list to store sentiment analysis results
sentiment_results = []

# Initialize the VADER sentiment analyzer for emotion analysis
analyzer = SentimentIntensityAnalyzer()

for record in data:
    title = record[0]  # Assuming the title is in the first column
    full_content = record[1]  # Assuming the full story content is in the second column

    # Perform sentiment analysis for the title
    title_blob = TextBlob(title)
    title_sentiment = title_blob.sentiment

    # Perform sentiment analysis for the full story content
    content_blob = TextBlob(full_content)
    content_sentiment = content_blob.sentiment

    # Classify sentiment polarity into labels (positive, negative, or neutral)
    def get_sentiment_label(polarity):
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"

    title_sentiment_label = get_sentiment_label(title_sentiment.polarity)
    content_sentiment_label = get_sentiment_label(content_sentiment.polarity)

    # Perform emotion analysis using VADER
    emotion_title = analyzer.polarity_scores(title)
    emotion_content = analyzer.polarity_scores(full_content)

    sentiment_results.append({
        'Title': title,
        'Title Sentiment Polarity': title_sentiment.polarity,
        'Title Sentiment Label': title_sentiment_label,
        'Full Content': full_content,
        'Content Sentiment Polarity': content_sentiment.polarity,
        'Content Sentiment Label': content_sentiment_label,
        'Title Emotion Analysis': emotion_title,
        'Content Emotion Analysis': emotion_content
    })

# Close the database connection
conn.close()

# Print or further process the sentiment analysis results
for result in sentiment_results:
    print("Title:", result['Title'])
    print("Title Sentiment Polarity:", result['Title Sentiment Polarity'])
    print("Title Sentiment Label:", result['Title Sentiment Label'])
    print("Full Content:", result['Full Content'])
    print("Content Sentiment Polarity:", result['Content Sentiment Polarity'])
    print("Content Sentiment Label:", result['Content Sentiment Label'])
    print("Title Emotion Analysis:", result['Title Emotion Analysis'])
    print("Content Emotion Analysis:", result['Content Emotion Analysis'])
    print()
