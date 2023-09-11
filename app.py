from flask import Flask, request, jsonify
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import requests
from fake_useragent import UserAgent

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot settings
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

# Initialize UserAgent
ua = UserAgent()

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
    user_agent = ua.random

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
