from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

app = Flask(__name__)
#ua = UserAgent()

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL not provided"}), 400

    # Set up Selenium with headless Chrome
    options = Options()
    options.headless = True

    # Set random user-agent
    #user_agent = ua.random
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")

    # Proxy setup if provided
    proxy = request.json.get('proxy')
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.set_page_load_timeout(30)  # Set timeout to 30 seconds
    html = driver.page_source
    driver.quit()

    # Parse with BeautifulSoup if 'parse' key is provided in request
    parsed_data = {}
    if request.json.get('parse'):
        soup = BeautifulSoup(html, 'html.parser')
        # Add your parsing logic here
        # Example: parsed_data['title'] = soup.title.string

    return jsonify({"html": html, "parsed_data": parsed_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
