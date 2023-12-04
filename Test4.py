import sqlite3
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt 

conn = sqlite3.connect('reddit_data.db')
cursor = conn.cursor()

cursor.execute("SELECT title, full_story, timestamp, username FROM reddit_posts")
data = cursor.fetchall()

sentiment_results = []

analyzer = SentimentIntensityAnalyzer()

timestamps = []
compound_scores = []

user_sentiment = {}

for record in data:
    title = record[0] 
    full_content = record[1]
    timestamp = record[2]
    username = record[3]  

    
    title_blob = TextBlob(title)
    title_sentiment = title_blob.sentiment

    content_blob = TextBlob(full_content)
    content_sentiment = content_blob.sentiment

    def get_sentiment_label(polarity):
        if polarity > 0.0:
            return "positive"
        elif polarity < 0.0:
            return "negative"
        else:
            return "neutral"

    title_sentiment_label = get_sentiment_label(title_sentiment.polarity)
    content_sentiment_label = get_sentiment_label(content_sentiment.polarity)

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

    timestamps.append(timestamp)
    compound_scores.append(content_sentiment.polarity)  

    if username not in user_sentiment:
        user_sentiment[username] = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

    user_sentiment[username][title_sentiment_label] += 1
    user_sentiment[username][content_sentiment_label] += 1

conn.close()

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

plt.figure(figsize=(10, 6))
plt.plot(timestamps, compound_scores, marker='o', linestyle='-', color='b')
plt.title('Sentiment Trends Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Compound Sentiment Score')
plt.xticks(rotation=45)
plt.grid()
plt.show()


for username, sentiment_data in user_sentiment.items():
    print(f"User: {username}")
    print("Positive Posts:", sentiment_data['positive'])
    print("Negative Posts:", sentiment_data['negative'])
    print("Neutral Posts:", sentiment_data['neutral'])
    print()
