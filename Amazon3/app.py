from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    url = request.form['url']
    reviews = scrape_amazon_reviews(url)
    return render_template('results.html', reviews=reviews)

def scrape_amazon_reviews(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    reviews = []

    # Find all review blocks
    review_blocks = soup.find_all('div', {'data-hook': 'review'})

    # Extract review text and rating from each review block
    for block in review_blocks:
        text = block.find('span', {'data-hook': 'review-body'}).get_text().strip()
        rating = block.find('i', {'data-hook': 'review-star-rating'}).get_text().split(' ')[0]
        reviews.append({'text': text, 'rating': rating})

    # Calculate sentiment for each review
    sid = SentimentIntensityAnalyzer()
    for review in reviews:
        sentiment_scores = sid.polarity_scores(review['text'])
        if sentiment_scores['compound'] > 0:
            review['sentiment'] = 'Positive'
        elif sentiment_scores['compound'] < 0:
            review['sentiment'] = 'Negative'
        else:
            review['sentiment'] = 'Neutral'

    return reviews
