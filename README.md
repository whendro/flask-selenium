# flask-selenium
docker build -t flask_selenium .
docker run -p 5000:5000 -v ./:/app flask_selenium
