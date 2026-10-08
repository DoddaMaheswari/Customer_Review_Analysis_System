from textblob import TextBlob
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import urllib.parse
import time


# --------------------------------------------------
# 1. CREATE SELENIUM DRIVER
# --------------------------------------------------

def create_driver():

    options = webdriver.ChromeOptions()

    # Run Chrome without opening the browser window
    options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--window-size=1920,1080")

    # Browser user agent
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


# --------------------------------------------------
# 2. AMAZON SCRAPER
# --------------------------------------------------

def scrape_amazon(product_name):

    reviews = []

    driver = None

    try:

        driver = create_driver()

        # Convert product name into URL format
        search_query = urllib.parse.quote_plus(product_name)

        search_url = f"https://www.amazon.in/s?k={search_query}"

        print("\nAmazon search URL:")
        print(search_url)

        # Open Amazon search page
        driver.get(search_url)

        time.sleep(4)

        # Find products
        products = driver.find_elements(
            By.CSS_SELECTOR,
            "div[data-component-type='s-search-result']"
        )

        product_url = None

        for product in products:

            try:

                link = product.find_element(
                    By.CSS_SELECTOR,
                    "a.a-link-normal.s-no-outline"
                )

                href = link.get_attribute("href")

                if href and "/dp/" in href:

                    product_url = href

                    break

            except Exception:
                continue

        if not product_url:

            print("Amazon product not found.")

            return []

        print("\nAmazon product URL:")
        print(product_url)

        # Open product page
        driver.get(product_url)

        time.sleep(4)

        # Scroll down
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(3)

        # Find reviews
        review_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span[data-hook='review-body']"
        )

        for element in review_elements[:10]:

            review = element.text.strip()

            if review:

                reviews.append(review)

        print("\nAmazon reviews found:", len(reviews))

    except Exception as e:

        print("\nAmazon error:", e)

    finally:

        if driver:

            driver.quit()

    return reviews


# --------------------------------------------------
# 3. FLIPKART SCRAPER
# --------------------------------------------------

def scrape_flipkart(product_name):

    reviews = []

    driver = None

    try:

        driver = create_driver()

        # Convert product name into URL format
        search_query = urllib.parse.quote_plus(product_name)

        search_url = (
            f"https://www.flipkart.com/search?q={search_query}"
        )

        print("\nFlipkart search URL:")
        print(search_url)

        # Open Flipkart search page
        driver.get(search_url)

        time.sleep(5)

        # Find product links
        product_links = driver.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/p/']"
        )

        product_url = None

        for link in product_links:

            href = link.get_attribute("href")

            if href and "/p/" in href:

                product_url = href

                break

        if not product_url:

            print("Flipkart product not found.")

            return []

        print("\nFlipkart product URL:")
        print(product_url)

        # Open product page
        driver.get(product_url)

        time.sleep(5)

        # Scroll down
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(3)

        # Find review elements
        review_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "div.ZmyHeo"
        )

        for element in review_elements[:10]:

            review = element.text.strip()

            if review:

                reviews.append(review)

        print("\nFlipkart reviews found:", len(reviews))

    except Exception as e:

        print("\nFlipkart error:", e)

    finally:

        if driver:

            driver.quit()

    return reviews


# --------------------------------------------------
# 4. SENTIMENT ANALYSIS
# --------------------------------------------------

def sentiment_analysis(reviews):

    sentiments = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    for review in reviews:

        analysis = TextBlob(review)

        polarity = analysis.sentiment.polarity

        if polarity > 0:

            sentiments["Positive"] += 1

        elif polarity < 0:

            sentiments["Negative"] += 1

        else:

            sentiments["Neutral"] += 1

    return sentiments


# --------------------------------------------------
# 5. DISPLAY SENTIMENT
# --------------------------------------------------

def display_sentiment(platform, sentiments):

    print(f"\n{platform} Sentiment Analysis")
    print("-" * 35)

    print(
        "Positive :",
        sentiments["Positive"]
    )

    print(
        "Negative :",
        sentiments["Negative"]
    )

    print(
        "Neutral  :",
        sentiments["Neutral"]
    )


# --------------------------------------------------
# 6. COMPARISON CHART
# --------------------------------------------------

def generate_chart(amazon, flipkart):

    labels = [
        "Positive",
        "Negative",
        "Neutral"
    ]

    amazon_values = [
        amazon.get(label, 0)
        for label in labels
    ]

    flipkart_values = [
        flipkart.get(label, 0)
        for label in labels
    ]

    x = range(len(labels))

    width = 0.35

    plt.figure(figsize=(9, 5))

    plt.bar(
        [i - width / 2 for i in x],
        amazon_values,
        width=width,
        label="Amazon"
    )

    plt.bar(
        [i + width / 2 for i in x],
        flipkart_values,
        width=width,
        label="Flipkart"
    )

    plt.xlabel("Sentiment")

    plt.ylabel("Number of Reviews")

    plt.title(
        "Amazon vs Flipkart Sentiment Analysis"
    )

    plt.xticks(
        x,
        labels
    )

    plt.legend()

    plt.tight_layout()

    plt.show()


# --------------------------------------------------
# 7. MAIN PROGRAM
# --------------------------------------------------

product_name = input(
    "Enter product name: "
)

print("\n" + "=" * 50)
print("CUSTOMER REVIEW ANALYSIS")
print("=" * 50)


# Amazon
amazon_reviews = scrape_amazon(
    product_name
)


# Flipkart
flipkart_reviews = scrape_flipkart(
    product_name
)


# --------------------------------------------------
# 8. PRINT REVIEWS
# --------------------------------------------------

print("\n")
print("=" * 50)
print("AMAZON REVIEWS")
print("=" * 50)

if amazon_reviews:

    for i, review in enumerate(
        amazon_reviews,
        start=1
    ):

        print(f"\n{i}. {review}")

else:

    print("No Amazon reviews found.")


print("\n")
print("=" * 50)
print("FLIPKART REVIEWS")
print("=" * 50)

if flipkart_reviews:

    for i, review in enumerate(
        flipkart_reviews,
        start=1
    ):

        print(f"\n{i}. {review}")

else:

    print("No Flipkart reviews found.")


# --------------------------------------------------
# 9. SENTIMENT ANALYSIS
# --------------------------------------------------

amazon_sentiments = sentiment_analysis(
    amazon_reviews
)

flipkart_sentiments = sentiment_analysis(
    flipkart_reviews
)


# --------------------------------------------------
# 10. DISPLAY RESULTS
# --------------------------------------------------

display_sentiment(
    "Amazon",
    amazon_sentiments
)

display_sentiment(
    "Flipkart",
    flipkart_sentiments
)


# --------------------------------------------------
# 11. GENERATE COMPARISON CHART
# --------------------------------------------------

if amazon_reviews or flipkart_reviews:

    generate_chart(
        amazon_sentiments,
        flipkart_sentiments
    )

else:

    print(
        "\nNo reviews available for visualization."
    )
    