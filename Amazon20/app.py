from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from textblob import TextBlob
import time

app = Flask(__name__)

# Define the route for the landing page
@app.route('/')
def index():
    return render_template('index.html')

# Define the route for the reviews page
@app.route('/reviews',methods = ['POST'])
def reviews():
    # Initialize a new Chrome web driver
    driver = webdriver.Firefox()

    url= request.form['url']
    # Navigate to the Amazon product page
    driver.get(url)

    # Scroll to the bottom of the page repeatedly until all reviews are loaded
    while True:
        # Get the current page height
        current_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load
        time.sleep(2)

        # Get the new page height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If the page height has not increased, all reviews have been loaded
        if new_height == current_height:
            break

    # Extract all the review elements
    reviews = []
    while True:
        review_elements = driver.find_elements(By.XPATH, '//div[@data-hook="review"]')

        # Extract the text of each review element and determine the sentiment
        for review_element in review_elements:
            review_text = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]').text
            review_blob = TextBlob(review_text)
            review_sentiment = review_blob.sentiment.polarity
            sentiment_label = "positive" if review_sentiment > 0 else "negative" if review_sentiment < 0 else "neutral"
            reviews.append((review_text, review_sentiment, sentiment_label))

        # Click the "Next page" button
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(text(),"Next page")]')
            next_button.click()

            # Wait for the page to load
            time.sleep(2)

        except:
            break

    # Close the web driver
    driver.quit()

    # Render the reviews template with the extracted reviews
    return render_template('reviews.html', reviews=reviews)

# Run the app on port 5000
if __name__ == '__main__':
    app.run(port=5000, debug=True)
