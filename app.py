from flask import Flask, request, jsonify
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import requests
import os
import random
from dotenv import load_dotenv
from user_agent import generate_user_agent


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.3",
    ]

# Initialize UserAgent
# ua = UserAgent()

def send_telegram_message(message):
    try:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=payload)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL not provided"}), 400

    # Random User-Agent for both Selenium and cloudscraper
    # user_agent = ua.random
    # user_agent = random.choice(USER_AGENTS)
    user_agent = generate_user_agent()



    # First, try with Selenium
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        page_source = driver.page_source
        driver.quit()
        return page_source
    except Exception as e:
        driver.quit()
        logger.error(f"Selenium failed: {e}")
        send_telegram_message(f"Selenium error: {e}")

    # If Selenium fails, fall back to cloudscraper
    scraper = cloudscraper.create_scraper(browser=user_agent)
    try:
        response = scraper.get(url)
        return response.text
    except Exception as e:
        logger.error(f"Cloudscraper failed: {e}")
        send_telegram_message(f"Cloudscraper error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
